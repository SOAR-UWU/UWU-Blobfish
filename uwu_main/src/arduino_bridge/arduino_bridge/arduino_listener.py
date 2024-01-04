import rclpy
from rclpy.node import Node
import os

from motor_msg.msg import Motors

from .arduino_interface import JetsonArduinoInterface
from .arduino_interface import BOARD_FQBN, BAUD_RATE, ARDUINO_FILES, ARDUINO_PORT
import serial
import subprocess

INO_FILE = os.path.join(ARDUINO_FILES, "main", "main.ino")


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
        ser = serial.Serial(ARDUINO_PORT, baudrate=BAUD_RATE)
        self.jai = JetsonArduinoInterface(ser)

        subprocess.run(["arduino-cli",
                        "compile",
                        "--fqbn",
                        BOARD_FQBN,
                        INO_FILE,
                        "--library",
                        ARDUINO_FILES], check=True)

        self.get_logger().info("Arduino code compiled")
        
        subprocess.run(["arduino-cli",
                        "upload",
                        "-p",
                        ARDUINO_PORT,
                        "--fqbn",
                        BOARD_FQBN,
                        INO_FILE], check=True)

        self.get_logger().info("Arduino code uploaded")

        self.jai.wait_for_connection(b'S', 0)
        self.get_logger().info("Connection established, Arduino bridge started")

    def listener_callback(self, msg):
        self.jai.write_motor_values([
            msg.motor_fr,
            msg.motor_mr,
            msg.motor_bm,
            msg.motor_bl,
            msg.motor_ml,
            msg.motor_br,
            msg.motor_fl])


def main(args=None):
    rclpy.init(args=args)

    bridge = ArduinoBridge()
    rclpy.spin(bridge)

    bridge.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
