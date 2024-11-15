import numpy as np
import rclpy
import rclpy.parameter
import rclpy.qos
from geometry_msgs.msg import Quaternion
from rcl_interfaces.msg import Log
from rclpy.node import Node
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

    def imu_callback(self, msg: CommonGroup):
        if self.is_calibrating:
            self.accum_calibration(msg)
            return
        if self.offset_rot is None or self.offset_grav is None:
            return

        raw_quat = msg.quaternion
        raw_rot = Rotation.from_quat((raw_quat.x, raw_quat.y, raw_quat.z, raw_quat.w))
        rot = self.offset_rot.inv() * raw_rot
        quat = rot.as_quat()

        x, y, z = msg.accel.x, msg.accel.y, msg.accel.z
        x, y, z = remove_gravity_from_accel(raw_rot, self.offset_grav, x, y, z)

        self.state.p.orientation = Quaternion(
            x=quat[0], y=quat[1], z=quat[2], w=quat[3]
        )
        self.state.p.position.x = 0.0
        self.state.p.position.y = 0.0
        self.state.p.position.z = 0.0
        self.state.a.linear.x = x
        self.state.a.linear.y = y
        self.state.a.linear.z = z

        self.pub_imu()

    def start_calibration(self):
        self.is_calibrating = True
        self.__total = self.get_parameter("imu_num_cal_samples").value
        self.__count = 0
        self.__accum_quat = []
        self.__accum_grav = 0.0
        self.get_logger().info("Starting calibration...")

    def accum_calibration(self, msg: CommonGroup):
        # NOTE: The below assumes the robot is stationary during calibration in
        # order to calculate the gravitational acceleration.
        if self.__count >= self.__total:
            self.finalize_calibration()
            return
        self.__count += 1
        # TODO: Do IQR based filtering.
        quat = msg.quaternion
        acc_x, acc_y, acc_z = msg.accel.x, msg.accel.y, msg.accel.z
        self.__accum_grav += (acc_x**2 + acc_y**2 + acc_z**2) ** 0.5
        self.__accum_quat.append((quat.w, quat.x, quat.y, quat.z))

    def finalize_calibration(self):
        self.is_calibrating = False
        w, x, y, z = average_quaternions(np.array(self.__accum_quat))
        self.offset_rot = Rotation.from_quat((x, y, z, w))
        self.offset_grav = self.__accum_grav / self.__total
        self.__accum_quat = None
        r, p, h = self.offset_rot.as_euler("xyz", degrees=True)
        self.get_logger().info(
            f"Calibrated offsets r: {r:6.1f}\tp: {p:6.1f}\th: {h:6.1f}\tg: {self.offset_grav:4.3f}"
        )

    def keypress_callback(self, msg: Char):
        keypress = chr(msg.data)
        if self.is_calibrating:
            self._confirm_cal = False
        if keypress == "h":
            if self.is_calibrating:
                self.log_kp("Currently calibrating...")
            else:
                self.log_kp("Press [ to start calibration.")
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


def main(args=None):
    rclpy.init(args=args)

    node = IMUCalculationNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
