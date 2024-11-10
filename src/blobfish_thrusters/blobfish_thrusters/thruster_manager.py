import numpy as np
import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.qos import qos_profile_sensor_data
from scipy.spatial.transform import Rotation
from std_msgs.msg import Char

from blobfish_msgs.msg import Motors

# ESCs use Arduino Servo, values taken from BlueRobotics Basic ESCs specs:
SERVO_NEUTRAL = 1500
SERVO_FULL_REV = 1100
SERVO_FULL_FWD = 1900

# fmt: off
# The following section reads the motor positions and directions from the
# parameter server and orders the motors in the correct order in the matrix.
# The ROS param <motor_name>_order should be a number from 1 to 7, denoting
# the number of that motor based on the motor_msg.
MOTOR_VECTOR_MATRIX = {
    # r p h x y z 
    "fl": [   0,   0,  -1,   1,   0,   0],
    "fr": [   0,   0,   1,   1,   0,   0],
    "ml": [   1,   0,   0,   0,   0,  -1],
    "mr": [  -1,   0,   0,   0,   0,  -1],
    "bl": [   0,   0,   1,  -1,   0,   0],
    "br": [   0,   0,  -1,  -1,   0,   0],
    "bm": [   0,  -1,   0,   0,   0,   0],
}
# fmt: on


class Thruster_Manager(Node):
    def __init__(self):
        super().__init__("thruster_manager")

        # Check the config file for the actual values of these parameters

        # Order, meaning the mapping from motor position to motor number on Arduino.
        self.declare_parameter("fl_order", Parameter.Type.INTEGER)
        self.declare_parameter("fr_order", Parameter.Type.INTEGER)
        self.declare_parameter("ml_order", Parameter.Type.INTEGER)
        self.declare_parameter("mr_order", Parameter.Type.INTEGER)
        self.declare_parameter("bl_order", Parameter.Type.INTEGER)
        self.declare_parameter("br_order", Parameter.Type.INTEGER)
        self.declare_parameter("bm_order", Parameter.Type.INTEGER)

        # Get the values of the declared parameters
        self.motor_names = [f"motor_{num}" for num in range(1, 8)]

        motor_orders = []
        for motor_name, motor_vector in MOTOR_VECTOR_MATRIX.items():
            motor_vector = np.array(motor_vector)
            motor_pos = self.get_parameter(f"{motor_name}_order")
            motor_orders.append((motor_pos.value, motor_vector))

        motor_orders.sort(key=lambda x: x[0])

        arr = [motor[1] for motor in motor_orders]

        self.motor_matrix = np.array(arr, dtype=np.float64)

        self.scale = 300  # how much to scale the pid value
        self.create_subscription(
            Twist,
            "blobfish/control_effort",
            self.calculate_thrusters,
            qos_profile_sensor_data,
        )
        self.create_subscription(
            Twist,
            "blobfish/imu_measurements",
            self.set_rotation,
            qos_profile_sensor_data,
        )
        self.create_subscription(Char, "keypress", self.toggle_motors, 10)
        self.motor_publisher = self.create_publisher(
            Motors, "blobfish/motor_values", 10
        )
        self.get_logger().info("Thruster manager started")
        self.stopped = False

    def set_rotation(self, msg: Twist):
        rot = Rotation.from_euler(
            "xyz", [msg.angular.x, msg.angular.y, msg.angular.z], degrees=True
        )
        self.orientation = rot

    def toggle_motors(self, msg):
        keypress = chr(msg.data)
        if keypress == " ":
            self.stopped = not self.stopped
            self.get_logger().info(f"Motors running: {not self.stopped}")
        elif keypress == "h":
            self.get_logger().info("Press SPACE to turn off/on the motors")

    def calculate_thrusters(self, pid_msg):
        if self.stopped:
            motor_vals = Motors()
            for i, name in enumerate(self.motor_names):
                setattr(motor_vals, name, SERVO_NEUTRAL)
            self.motor_publisher.publish(motor_vals)
            return

        angular_pid = np.array(
            [pid_msg.angular.x, pid_msg.angular.y, pid_msg.angular.z]
        )
        linear_pid = np.array([pid_msg.linear.x, pid_msg.linear.y, pid_msg.linear.z])
        linear_pid = self.orientation.apply(linear_pid, inverse=True)
        pid_weights = np.concatenate((angular_pid, linear_pid)).reshape(-1, 1)
        pid_vec = (self.motor_matrix @ pid_weights).flatten()
        scaled_pid_vec = np.multiply(self.scale, pid_vec)

        out_vec = (scaled_pid_vec + SERVO_NEUTRAL).clip(SERVO_FULL_REV, SERVO_FULL_FWD)

        motor_vals = Motors()
        for i, name in enumerate(self.motor_names):
            setattr(motor_vals, name, int(out_vec[i]))
        self.motor_publisher.publish(motor_vals)


def main(args=None):
    rclpy.init(args=args)

    manager = Thruster_Manager()
    try:
        rclpy.spin(manager)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
