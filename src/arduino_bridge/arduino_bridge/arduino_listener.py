import rclpy
from rclpy.node import Node
import os

from blobfish_msgs.msg import Motors

from .arduino_interface import JetsonArduinoInterface
import serial
import subprocess


class ArduinoBridge(Node):
    def __init__(self):
        super().__init__("arduino_bridge")
        self.subscription = self.create_subscription(
            Motors,
            "blobfish/motor_values",
            self.listener_callback,
            10
        )
        self.declare_parameter('arduino_files', "/workspaces/isaac_ros-dev/arduino")
        self.declare_parameter('arduino_port', "/dev/ttyUSB1")
        self.declare_parameter("baud_rate", 19200)
        self.declare_parameter("board_fqbn", "arduino:avr:nano:cpu=atmega328old")
        ARDUINO_FILES = self.get_parameter("arduino_files").value
        ARDUINO_PORT = self.get_parameter("arduino_port").value
        BAUD_RATE = self.get_parameter("baud_rate").value
        BOARD_FQBN = self.get_parameter("board_fqbn").value
        INO_FILE = os.path.join(ARDUINO_FILES, "main", "main.ino")

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
            msg.motor_1,
            msg.motor_2,
            msg.motor_3,
            msg.motor_4,
            msg.motor_5,
            msg.motor_6,
            msg.motor_7])


def main(args=None):
    rclpy.init(args=args)

    bridge = ArduinoBridge()
    rclpy.spin(bridge)

    bridge.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
