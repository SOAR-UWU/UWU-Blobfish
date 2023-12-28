import rclpy
from rclpy.node import Node

from motor_msg.msg import Motors

from .arduino_interface import JetsonArduinoInterface
import serial


class ArduinoBridge(Node):
    def __init__(self):
        super().__init__("arduino_bridge")
        self.subscription = self.create_subscription(
            Motors,
            "motor_values",
            self.listener_callback,
            10
        )
        self.subscription   # prevent unused variable warning
        ser = serial.Serial("/dev/ttyUSB0")
        self.jai = JetsonArduinoInterface(ser)
        self.jai.wait_for_connection(b'S', 0)
        self.get_logger().info("Arduino bridge started")

    def listener_callback(self, msg):
        self.jai.write_motor_values([
            msg.motor1,
            msg.motor2,
            msg.motor3,
            msg.motor4,
            msg.motor5,
            msg.motor6,
            msg.motor7])


def main(args=None):
    rclpy.init(args=args)

    bridge = ArduinoBridge()
    rclpy.spin(bridge)

    bridge.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
