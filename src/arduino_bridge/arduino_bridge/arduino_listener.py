import time
import rclpy
import rclpy.qos
from rclpy.node import Node
from std_msgs.msg import Float32
import os
from rclpy.parameter import Parameter

from blobfish_msgs.msg import Motors

from .arduino_interface import JetsonArduinoInterface
import serial
import subprocess

# TODO: Benchmark maximum rate possible of sending motor values to Arduino.
# Napkin maths:
# 19200 baudrate = 2400 bytes per second
# 7 motors * 2 bytes per uint16 + 2 bytes start/end = 16 bytes per message
# 2400 / 16 = 150 messages per second
MOTOR_UPDATE_RATE = 90
MOTOR_NEUTRAL = 1500
MOTOR_TOPIC = "/blobfish/motor_values"
SAFETY_TIMEOUT = 0.5  # Set motors to neutral after seconds of no messages
QOS = rclpy.qos.qos_profile_sensor_data

# TODO: Add magic version number to main.ino so we can detect if necessary to compile
# and upload new code.

class ArduinoBridge(Node):
    def __init__(self):
        super().__init__("arduino_bridge")
        self.subscription = self.create_subscription(
            Motors, MOTOR_TOPIC, self.listener_callback, QOS
        )
        self.depth_publisher = self.create_publisher(Float32, "depth", 0)
        self.declare_parameter('arduino_files', Parameter.Type.STRING)
        self.declare_parameter('arduino_port', Parameter.Type.STRING)
        self.declare_parameter("baud_rate", Parameter.Type.INTEGER)
        self.declare_parameter("board_fqbn", Parameter.Type.STRING)
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
        
        successful = False
        while not successful:
            try:
                subprocess.run(["arduino-cli",
                                "upload",
                                "-p",
                                ARDUINO_PORT,
                                "--fqbn",
                                BOARD_FQBN,
                                INO_FILE], check=True)
                successful = True
            except:
                pass

        self.get_logger().info("Arduino code uploaded")

        self.jai.wait_for_connection(b'S', 0)
        self.get_logger().info("Connection established, Arduino bridge started")

        self.motors = [MOTOR_NEUTRAL] * 7
        self.__last_msg_time = time.time()
        self.create_timer(1 / MOTOR_UPDATE_RATE, self.update_motors)

    def listener_callback(self, msg: Motors):
        self.__last_msg_time = time.time()
        for i in range(7):
            self.motors[i] = getattr(msg, f"motor_{i+1}")
        
    def update_motors(self):
        # Stop motors if no messages received for SAFETY_TIMEOUT seconds
        if time.time() - self.__last_msg_time > SAFETY_TIMEOUT:
            self.motors = [MOTOR_NEUTRAL] * 7
        self.jai.write_motor_values(self.motors)
        
    def check_depth_value(self):
        depth = self.jai.read_depth_value()
        if depth is None:
            return None
        msg = Float32()
        msg.data = float(depth)
        self.depth_publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)

    bridge = ArduinoBridge()
    try:
        rclpy.spin(bridge)
        # while rclpy.ok():
        #     rclpy.spin_once(bridge, timeout_sec=0.01)
        #     bridge.check_depth_value()
    except KeyboardInterrupt:
        pass
    finally:
        # Stop the motors on shutdown.
        bridge.jai.write_motor_values([MOTOR_NEUTRAL] * 7)
        bridge.jai.ser.close()


if __name__ == "__main__":
    main()
