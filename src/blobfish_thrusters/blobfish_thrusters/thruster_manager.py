import numpy as np
import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.qos import qos_profile_sensor_data as QOS
from std_msgs.msg import Char

from blobfish_msgs.msg import Motors, MotorsFloat

# TODO: Put safe, non-max values here.
# ESCs use Arduino Servo, values taken from BlueRobotics Basic ESCs specs:
SERVO_NEUTRAL = 1500
SERVO_FULL_REV = 1100
SERVO_FULL_FWD = 1900
# Ratio of full speed range to use as the normal max speed when control effort is 1.
# When final control effort exceeds 1, it can go pass the expected normal max speed,
# so use SERVO_FULL_REV and SERVO_FULL_FWD as the true max speed.
SPD_RATIO = 1.0

# fmt: off
MOTOR_VECTOR_MATRIX = {
    # row pitch yaw forward lateral depth 
    "fl": [   0,   0,  -1,   1,   0,   0],
    "fr": [   0,   0,   1,   1,   0,   0],
    "ml": [   1,   0,   0,   0,   0,  -1],
    "mr": [  -1,   0,   0,   0,   0,  -1],
    "bl": [   0,   0,   1,  -1,   0,   0],
    "br": [   0,   0,  -1,  -1,   0,   0],
    "bm": [   0,  -1,   0,   0,   0,   0],
}
# fmt: on
# Attribute names of each motor in the blobfish_msgs/Motors message.
MOTOR_MSG_NAMES = [f"motor_{num}" for num in range(1, 8)]

PID_TOPIC = "/blobfish/control_effort"
MOTOR_TOPIC = "/blobfish/motor_values"
DEBUG_TOPIC = "/blobfish/motor_floats"
KEYPRESS_TOPIC = "/keypress"

NODE_NAME = "thruster_manager"


class ThrusterManager(Node):
    def __init__(self):
        super(ThrusterManager, self).__init__(NODE_NAME)

        # Order, meaning the mapping from motor position to motor number on Arduino.
        for name in MOTOR_VECTOR_MATRIX:
            self.declare_parameter(f"{name}_order", Parameter.Type.INTEGER)

        self.create_subscription(Twist, PID_TOPIC, self.calculate_thrusters, QOS)
        self.create_subscription(Char, KEYPRESS_TOPIC, self.toggle_motors, 10)
        motors_publisher = self.create_publisher(Motors, MOTOR_TOPIC, 0)
        self.pub_floats = self.create_publisher(MotorsFloat, DEBUG_TOPIC, 0)

        # Reorder the motor vector matrix based on the order of the motors.
        # Parameter order must be 0-indexed. 7, 6 refers to 7 motors, 6 DoFs.
        self.motor_matrix = np.zeros((7, 6), dtype=np.float64)
        for name, vector in MOTOR_VECTOR_MATRIX.items():
            motor_pos = self.get_parameter(f"{name}_order").value
            self.motor_matrix[motor_pos] = np.array(vector)

        # Whether all motors should be stopped.
        self.stopped = False
        # Reused for each message.
        self.motor_vals = Motors()
        self.pub_motors = lambda: motors_publisher.publish(self.motor_vals)

        self.get_logger().info("Thruster manager started")

    def toggle_motors(self, msg: Char):
        keypress = chr(msg.data)
        if keypress == " ":
            self.stopped = not self.stopped
            self.get_logger().info(f"Motors running: {not self.stopped}")
        elif keypress == "h":
            self.get_logger().info("Press SPACE to turn off/on the motors")

    def publish_debug_floats(self, vals: np.ndarray):
        out = MotorsFloat()
        for name in MOTOR_VECTOR_MATRIX:
            motor_pos = self.get_parameter(f"{name}_order").value
            setattr(out, name, vals[motor_pos])
        self.pub_floats.publish(out)

    def calculate_thrusters(self, msg: Twist):
        # All pid values are in the range [-1, 1].
        # x is forward, y is lateral, z is depth
        linear_pid = np.array([msg.linear.x, msg.linear.y, msg.linear.z])
        angular_pid = np.array([msg.angular.x, msg.angular.y, msg.angular.z])
        pid_weights = np.concatenate((angular_pid, linear_pid)).reshape(-1, 1)
        # Should be roughly [-1, 1] but can exceed.
        out_vals: np.ndarray = (self.motor_matrix @ pid_weights).flatten()
        self.publish_debug_floats(out_vals)

        # Scale negative values by negative range and positive values by positive range.
        out_vals *= SPD_RATIO
        out_vals[out_vals < 0] *= abs(SERVO_NEUTRAL - SERVO_FULL_REV)
        out_vals[out_vals > 0] *= abs(SERVO_NEUTRAL - SERVO_FULL_FWD)
        out_vals += SERVO_NEUTRAL
        out_vals = out_vals.clip(SERVO_FULL_REV, SERVO_FULL_FWD)

        # If motors are stopped, set all values to neutral.
        # Do it this way instead of early return so can debug out_vals.
        out_vals = np.full_like(out_vals, SERVO_NEUTRAL) if self.stopped else out_vals

        for name, val in zip(MOTOR_MSG_NAMES, out_vals):
            setattr(self.motor_vals, name, round(val))
        self.pub_motors()


def main(args=None):
    rclpy.init(args=args)

    node = ThrusterManager()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
