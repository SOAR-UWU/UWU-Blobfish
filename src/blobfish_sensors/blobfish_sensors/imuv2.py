import numpy as np
import rclpy
import rclpy.parameter
import rclpy.qos
from rcl_interfaces.msg import Log
from rclpy.node import Node
from rclpy.time import Time
from scipy.spatial.transform import Rotation
from std_msgs.msg import Char
from vectornav_msgs.msg import CommonGroup

from blobfish_msgs.msg import Kinematics

from .util import average_quaternions, remove_gravity_from_accel

NODE_NAME = "imu_calculator"

VN_TOPIC = "/vectornav/raw/common"
IMU_TOPIC = "/blobfish/imu_measurements"
KEYPRESS_TOPIC = "/keypress"
KEYPRESS_OUT_TOPIC = "/kpout"

# TODO: separate method to calibrate IMU & gravity from recentering

QOS = rclpy.qos.qos_profile_sensor_data


class IMUCalculationNode(Node):
    def __init__(self):
        super(IMUCalculationNode, self).__init__(NODE_NAME)

        # TODO: make it optionally time duration based instead?
        self.declare_parameter("imu_num_cal_samples", 400)

        self.create_subscription(CommonGroup, VN_TOPIC, self.imu_callback, QOS)
        self.create_subscription(Char, KEYPRESS_TOPIC, self.keypress_callback, 10)

        _imu_pub = self.create_publisher(Kinematics, IMU_TOPIC, 0)
        _kp_log_pub = self.create_publisher(Log, KEYPRESS_OUT_TOPIC, 10)

        self.state = Kinematics()
        self.log_kp = lambda x: _kp_log_pub.publish(Log(name=self.get_name(), msg=x))
        self.pub_imu = lambda: _imu_pub.publish(self.state)

        self.offset_rot = None
        self.offset_grav = None

        self.start_calibration()

    # TODO: Consider higher/arbitrary precision floats for better accuracy.
    def imu_callback(self, msg: CommonGroup):
        if self.is_calibrating:
            self.accum_calibration(msg)
            return
        if self.offset_rot is None or self.offset_grav is None:
            return

        # Apply rotation offset.
        raw_quat = msg.quaternion
        raw_rot = Rotation.from_quat((raw_quat.x, raw_quat.y, raw_quat.z, raw_quat.w))
        rot = self.offset_rot.inv() * raw_rot
        qx, qy, qz, qw = rot.as_quat()

        # Remove gravity effect & rotate from local to global frame.
        ax, ay, az = msg.accel.x, msg.accel.y, msg.accel.z
        ax, ay, az = remove_gravity_from_accel(raw_rot, self.offset_grav, ax, ay, az)
        ax, ay, az = raw_rot.apply((ax, ay, az))

        self.state.a.linear.x = ax
        self.state.a.linear.y = ay
        self.state.a.linear.z = az

        self.state.p.orientation.x = qx
        self.state.p.orientation.y = qy
        self.state.p.orientation.z = qz
        self.state.p.orientation.w = qw

        t = Time.from_msg(msg.header.stamp)
        self.accum_accel(ax, ay, az, t)

        self.pub_imu()

    def accum_accel(self, ax: float, ay: float, az: float, t: Time):
        try:
            lt = self.__last_t
        except AttributeError:
            self.__last_t = t
            return
        self.__last_t = t

        dt = (t - lt).nanoseconds
        if dt < 0:
            self.get_logger().error(
                f"Negative time delta! t={t}, lt={lt}, dt={dt}",
                skip_first=True,
                throttle_duration_sec=2.0,
            )
        v = self.state.v.linear
        p = self.state.p.position

        p.x += v.x * dt * 1e-9
        p.y += v.y * dt * 1e-9
        p.z += v.z * dt * 1e-9
        v.x += ax * dt * 1e-9
        v.y += ay * dt * 1e-9
        v.z += az * dt * 1e-9

    def start_calibration(self):
        self.is_calibrating = True
        self.__count = self.get_parameter("imu_num_cal_samples").value
        self.__accum_quat = []
        self.__accum_grav = []
        self.get_logger().info("Starting calibration...")

    def accum_calibration(self, msg: CommonGroup):
        # NOTE: The below assumes the robot is stationary during calibration in
        # order to calculate the gravitational acceleration.
        if self.__count <= 0:
            self.finalize_calibration()
            return
        self.__count -= 1
        # TODO: Do IQR based filtering.
        quat = msg.quaternion
        acc_x, acc_y, acc_z = msg.accel.x, msg.accel.y, msg.accel.z
        self.__accum_grav.append((acc_x**2 + acc_y**2 + acc_z**2) ** 0.5)
        self.__accum_quat.append((quat.w, quat.x, quat.y, quat.z))

    def finalize_calibration(self):
        self.is_calibrating = False
        qw, qx, qy, qz = average_quaternions(np.array(self.__accum_quat))
        self.offset_rot = Rotation.from_quat((qx, qy, qz, qw))
        self.offset_grav = np.mean(self.__accum_grav)
        self.__accum_quat = None
        self.__accum_grav = None
        r, p, h = self.offset_rot.as_euler("xyz", degrees=True)
        self.get_logger().info(
            f"Calibrated offsets r: {r:6.1f}\tp: {p:6.1f}\th: {h:6.1f}\tg: {self.offset_grav:4.3f}"
        )

    def recenter(self):
        self.state.v.linear.x = 0.0
        self.state.v.linear.y = 0.0
        self.state.v.linear.z = 0.0
        self.state.p.position.x = 0.0
        self.state.p.position.y = 0.0
        self.state.p.position.z = 0.0
        self.get_logger().info("Recentered!")

    def keypress_callback(self, msg: Char):
        keypress = chr(msg.data)
        if self.is_calibrating:
            self._confirm_cal = False
        if keypress == "h":
            if self.is_calibrating:
                self.log_kp("Currently calibrating...")
            else:
                self.log_kp("Press [ to start calibration.")
                self.log_kp("Press \\ to recenter.")
        elif keypress == "[" and not self.is_calibrating:
            self._confirm_cal = True
            self.log_kp("Press ] to confirm calibration.")
        elif (
            keypress == "]"
            and not self.is_calibrating
            and getattr(self, "_confirm_cal", False)
        ):
            self.start_calibration()
            self.log_kp("Confirmed calibration.")
        elif keypress == "\\":
            self.recenter()
            self.log_kp("Recentered!")


def main(args=None):
    rclpy.init(args=args)

    node = IMUCalculationNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
