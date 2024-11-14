"""Yeah, this isn't a generic topic monitor yet, it just monitors motor & IMU really well.

Say why aren't we using RViz?
"""

import getchlib
import rclpy
import rclpy.qos
import rich
from geometry_msgs.msg import Twist
from rcl_interfaces.msg import Log
from rclpy.node import Node
from std_msgs.msg import Char, String
from vectornav_msgs.msg import CommonGroup

from blobfish_msgs.msg import Motors, MotorsFloat

NODE_NAME = "monitor"

IMU_RAW_TOPIC = "/vectornav/raw/common"
IMU_PROC_TOPIC = "/blobfish/imu_measurements"
MOTOR_DEBUG_TOPIC = "/blobfish/motor_floats"
MOTOR_ACTUAL_TOPIC = "/blobfish/motor_values"
MOTOR_ORDER_TOPIC = "/blobfish/motor_order"
ROSOUT_TOPIC = "/rosout"
KEYPRESS_OUT_TOPIC = "/kpout"
KEYPRESS_TOPIC = "/keypress"
QOS = rclpy.qos.qos_profile_sensor_data

# TODO:
# - why aren't we using RViz/RQT?
# - OG keypress node should use keypress out too
# - tmux shell scripts for sim, irl & sim-irl testing


class MonitorNode(Node):
    def __init__(self):
        super(MonitorNode, self).__init__(NODE_NAME)

        self.create_subscription(CommonGroup, IMU_RAW_TOPIC, self.imu_raw_callback, QOS)
        self.create_subscription(Twist, IMU_PROC_TOPIC, self.imu_proc_callback, QOS)
        self.create_subscription(
            MotorsFloat, MOTOR_DEBUG_TOPIC, self.motor_debug_callback, QOS
        )
        self.create_subscription(
            Motors, MOTOR_ACTUAL_TOPIC, self.motor_actual_callback, QOS
        )
        self.create_subscription(
            String, MOTOR_ORDER_TOPIC, self.motor_order_callback, 10
        )
        self.create_subscription(Log, ROSOUT_TOPIC, self.rosout_callback, 10)
        self.create_subscription(
            Log, KEYPRESS_OUT_TOPIC, self.keypress_out_callback, 10
        )

        self.__key_pub = self.create_publisher(Char, KEYPRESS_TOPIC, 10)

    def imu_raw_callback(self, msg: CommonGroup):
        rich.print(msg)

    def imu_proc_callback(self, msg: Twist):
        rich.print(msg)

    def motor_debug_callback(self, msg: MotorsFloat):
        rich.print(msg)

    def motor_actual_callback(self, msg: Motors):
        rich.print(msg)

    def motor_order_callback(self, msg: String):
        rich.print(msg)

    def rosout_callback(self, msg: Log):
        rich.print(msg)

    def keypress_out_callback(self, msg: Log):
    def get_key(self) -> str:
        return getchlib.getkey(False, echo=False)


def main(args=None):
    rclpy.init(args=args)
    node = MonitorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
