"""Yeah, this isn't a generic topic monitor yet, it just monitors motor & IMU really well.

Say why aren't we using RViz?
"""

import logging

import getchlib
import rclpy
import rclpy.qos
import rich
from geometry_msgs.msg import Twist
from rcl_interfaces.msg import Log
from rclpy.node import Node
from rich.live import Live
from rich.logging import RichHandler
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
ROSOUT_LOG_LEVEL = logging.INFO

# TODO:
# - why aren't we using RViz/RQT?
# - OG keypress node should use keypress out too
# - tmux shell scripts for sim, irl & sim-irl testing


class MonitorNode(Node):
    def __init__(self, live: Live):
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
        self.__key_timer = self.create_timer(1 / 60, self.key_timer_callback)
        self.__live = live
        self.__handler = RichHandler(
            rich_tracebacks=True,
            tracebacks_suppress=[rclpy],
            console=live.console,
            show_path=False,
        )

    def imu_raw_callback(self, msg: CommonGroup):
        pass

    def imu_proc_callback(self, msg: Twist):
        pass

    def motor_debug_callback(self, msg: MotorsFloat):
        pass

    def motor_actual_callback(self, msg: Motors):
        pass

    def motor_order_callback(self, msg: String):
        pass

    def rosout_callback(self, msg: Log):
        # TODO: how to map original time & file location to Rich logging?
        # msg.stamp, msg.level, msg.name, msg.msg, msg.file, msg.function, msg.line
        log = logging.getLogger(f"rosout/{msg.name}")
        log.setLevel(ROSOUT_LOG_LEVEL)
        log.addHandler(self.__handler)
        if log.level == Log.DEBUG:
            log.debug(msg.msg)
        elif log.level == Log.INFO:
            log.info(msg.msg)
        elif log.level == Log.WARN:
            log.warning(msg.msg)
        elif log.level == Log.ERROR:
            log.error(msg.msg)
        elif log.level == Log.FATAL:
            log.critical(msg.msg)
        else:
            log.info(msg.msg)

    def keypress_out_callback(self, msg: Log):
        log = logging.getLogger(f"keypress_out/{msg.name}")
        log.setLevel(logging.INFO)
        log.addHandler(self.__handler)
        log.info(msg.msg)

    def key_timer_callback(self):
        key = self.get_key()
        if key is not None:
            msg = Char()
            msg.data = ord(key)
            self.__key_pub.publish(msg)

    def get_key(self):
        ch: str = getchlib.getkey(False, echo=False)
        return None if ch == "" else ch


def main(args=None):
    rclpy.init(args=args)
    with Live(refresh_per_second=10, screen=False) as live:
        node = MonitorNode(live)
        try:
            rclpy.spin(node)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
