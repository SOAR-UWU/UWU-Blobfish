"""Yeah, this isn't a generic topic monitor yet, it just monitors motor & IMU really well.

Say why aren't we using RViz?
"""

import itertools
import json
import logging
import os
import time
from collections import defaultdict, deque

import getchlib
import numpy as np
import rclpy
import rclpy.qos
from geometry_msgs.msg import Twist
from rcl_interfaces.msg import Log
from rclpy.node import Node
from rich.console import Console, ConsoleOptions
from rich.layout import Layout
from rich.live import Live
from rich.logging import RichHandler
from rich.panel import Panel
from rich.text import Text
from scipy.spatial.transform import Rotation
from std_msgs.msg import Char, String
from vectornav_msgs.msg import CommonGroup

from blobfish_msgs.msg import Kinematics, Motors, MotorsFloat

NODE_NAME = "monitor"

IMU_RAW_TOPIC = "/vectornav/raw/common"
IMU_CAL_TOPIC = "/blobfish/imu_measurements"
PID_TOPIC = "/blobfish/control_effort"
MOTOR_DEBUG_TOPIC = "/blobfish/motor_floats"
MOTOR_ACTUAL_TOPIC = "/blobfish/motor_values"
MOTOR_ORDER_TOPIC = "/blobfish/motor_order"
ROSOUT_TOPIC = "/rosout"
KEYPRESS_OUT_TOPIC = "/kpout"
KEYPRESS_TOPIC = "/keypress"

QOS = rclpy.qos.qos_profile_sensor_data
ROSOUT_LOG_LEVEL = logging.INFO
RATE = 30


class MonitorNode(Node):
    def __init__(self, live: Live):
        super(MonitorNode, self).__init__(NODE_NAME)

        self.create_subscription(CommonGroup, IMU_RAW_TOPIC, self.imu_raw_callback, QOS)
        self.create_subscription(Kinematics, IMU_CAL_TOPIC, self.imu_cal_callback, QOS)
        self.create_subscription(
            MotorsFloat, MOTOR_DEBUG_TOPIC, self.motor_debug_callback, QOS
        )
        self.create_subscription(
            Motors, MOTOR_ACTUAL_TOPIC, self.motor_actual_callback, QOS
        )
        self.create_subscription(Twist, PID_TOPIC, self.pid_callback, QOS)
        self.create_subscription(
            String, MOTOR_ORDER_TOPIC, self.motor_order_callback, 10
        )
        self.create_subscription(Log, ROSOUT_TOPIC, self.rosout_callback, 10)
        self.create_subscription(
            Log, KEYPRESS_OUT_TOPIC, self.keypress_out_callback, 10
        )
        self.__key_pub = self.create_publisher(Char, KEYPRESS_TOPIC, 10)
        self.create_layout(live)
        self.create_timer(1 / RATE, self.update_display)

    def create_layout(self, live: Live):
        L = Layout()
        rosout = ConsolePanel()
        kpout = ConsolePanel()
        text_motors = Text("no data yet")
        text_imu_cal = Text("no data yet")
        text_imu_raw = Text("no data yet")
        text_fps = Text("no data yet")
        imu_raw = Panel(text_imu_raw, title="VN-100")
        imu_cal = Panel(text_imu_cal, title="Calibrated")
        motors = Panel(text_motors, title="Motors")
        fps = Panel(text_fps, title="FPS")

        L.split_column(
            Layout(name="imu", size=5),
            Layout(motors, name="motor", size=5),
            Layout(fps, name="fps", size=3),
            Layout(name="log"),
            # Layout(name="keypress"),
        )
        L["imu"].split_row(
            Layout(imu_raw, name="raw"),
            Layout(imu_cal, name="cal"),
        )
        L["log"].split_row(
            Layout(Panel(rosout, title="rosout"), name="rosout", ratio=7),
            Layout(Panel(kpout, title="keypress"), name="kpout", ratio=3),
        )

        live.update(L)

        self.__live = live
        self.__text_imu_raw = text_imu_raw
        self.__text_imu_cal = text_imu_cal
        self.__text_motors = text_motors
        self.__text_fps = text_fps
        self.__rate_buf = defaultdict(lambda: deque(maxlen=10))
        self.__rate_last = defaultdict(int)
        self.__rate_fps = defaultdict(int)
        self.__motor_order = None
        self.__motor_debug_str = "No motor percent data yet\n"
        self.__motor_actual_str = "No motor data yet\n"
        self.__pid_str = "No PID data yet\n"
        self.__imu_raw_str = "No IMU data yet\n"
        self.__imu_cal_str = "No IMU calibrated data yet\n"
        self.__handler = RichHandler(
            rich_tracebacks=True,
            tracebacks_suppress=[rclpy],
            log_time_format="[%X]",
            console=rosout,
            show_path=False,
        )
        self.__kp_handler = RichHandler(
            rich_tracebacks=True,
            tracebacks_suppress=[rclpy],
            console=kpout,
            show_time=False,
            show_level=False,
            show_path=False,
        )

    def track_rate(self, name):
        last = self.__rate_last[name]
        now = time.time()
        self.__rate_buf[name].append(now - last)
        self.__rate_last[name] = now
        fps = 1 / max(1e-8, np.mean(self.__rate_buf[name]))
        self.__rate_fps[name] = fps

    def imu_raw_callback(self, msg: CommonGroup):
        pos = msg.position  # Empty for VN-100
        acc = msg.accel
        quat = msg.quaternion
        rot = Rotation.from_quat((quat.x, quat.y, quat.z, quat.w))
        r, p, h = rot.as_euler("xyz", degrees=True)
        self.__imu_raw_str = (
            f" r: {r: 8.1f}\t p: {p: 8.1f}\t h: {h: 8.1f}\n"
            f" x: {pos.x: 8.3f}\t y: {pos.y: 8.3f}\t z: {pos.z: 8.3f}\n"
            f"ax: {acc.x: 8.3f}\tay: {acc.y: 8.3f}\taz: {acc.z: 8.3f}"
        )
        self.track_rate("imu_raw")

    def imu_cal_callback(self, msg: Kinematics):
        pos = msg.p.position
        acc = msg.a.linear
        quat = msg.p.orientation
        rot = Rotation.from_quat((quat.x, quat.y, quat.z, quat.w))
        r, p, h = rot.as_euler("xyz", degrees=True)
        self.__imu_cal_str = (
            f" r: {r: 8.1f}\t p: {p: 8.1f}\t h: {h: 8.1f}\n"
            f" x: {pos.x: 8.3f}\t y: {pos.y: 8.3f}\t z: {pos.z: 8.3f}\n"
            f"ax: {acc.x: 8.3f}\tay: {acc.y: 8.3f}\taz: {acc.z: 8.3f}"
        )
        self.track_rate("imu_cal")

    def motor_debug_callback(self, msg: MotorsFloat):
        fl, fr = msg.fl, msg.fr
        ml, mr = msg.ml, msg.mr
        bl, br = msg.bl, msg.br
        bm = msg.bm
        self.__motor_debug_str = (
            f"FL: {fl: 6.3f}\t\tFR: {fr: 6.3f}\t\t"
            f"ML: {ml: 6.3f}\t\tMR: {mr: 6.3f}\t\t"
            f"BL: {bl: 6.3f}\t\tBR: {br: 6.3f}\t\t"
            f"BM: {bm: 6.3f}\n"
        )
        self.track_rate("motor_debug")

    def motor_actual_callback(self, msg: Motors):
        N = 7
        if self.__motor_order is None:
            pairs = {f"m{i}": getattr(msg, f"motor_{i}") for i in range(1, N + 1)}
        else:
            pairs = {
                f"m{i} ({self.__motor_order[i - 1].upper()})": getattr(
                    msg, f"motor_{i}"
                )
                for i in range(1, N + 1)
            }
        self.__motor_actual_str = "\t".join((f"{k}: {v:04d}" for k, v in pairs.items()))
        self.track_rate("motor_actual")

    def motor_order_callback(self, msg: String):
        try:
            order = json.loads(msg.data)
            self.__motor_order = {v: k for k, v in order.items()}
        except json.JSONDecodeError:
            self.get_logger().error("Invalid JSON in motor order")
            self.__motor_order = None

    def pid_callback(self, msg: Twist):
        ang = msg.angular
        lin = msg.linear
        self.__pid_str = f"r: {ang.x: 6.3f}\tp: {ang.y: 6.1f}\th: {ang.z: 6.1f}\tf: {lin.x: 6.1f}\tl: {lin.y: 6.1f}\tz: {lin.z: 6.1f}\n"
        self.track_rate("pid")

    def rosout_callback(self, msg: Log):
        # msg.stamp, msg.level, msg.name, msg.msg, msg.file, msg.function, msg.line
        log = logging.getLogger(f"rosout/{msg.name}")
        if self.__handler not in log.handlers:
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
        if self.__kp_handler not in log.handlers:
            log.setLevel(logging.INFO)
            log.addHandler(self.__kp_handler)

        log.info(msg.msg)

    def get_key(self):
        ch: str = getchlib.getkey(False, echo=False)
        return None if ch == "" else ch

    def pub_key(self):
        key = self.get_key()
        if key is not None:
            for k in key:
                msg = Char()
                msg.data = ord(k)
                self.__key_pub.publish(msg)

    def update_display(self):
        self.pub_key()
        self.__text_imu_raw.plain = self.__imu_raw_str
        self.__text_imu_cal.plain = self.__imu_cal_str
        self.__text_motors.plain = (
            self.__pid_str + self.__motor_debug_str + self.__motor_actual_str
        )
        # self.__text_fps.plain = "FPS: " + "\t".join(
        #     f"{k}: {v: 5.1f}" for k, v in self.__rate_fps.items()
        # )
        self.__live.refresh()
        self.pub_key()


# Taken from https://stackoverflow.com/a/74134595
# Improved by @Interpause to preserve original formatting.
class ConsolePanel(Console):
    def __init__(self, *args, **kwargs):
        console_file = open(os.devnull, "w")
        super(ConsolePanel, self).__init__(
            record=True, file=console_file, *args, **kwargs
        )

    def __rich_console__(self, console: Console, options: ConsoleOptions):
        # NOTE: on resizing, the linebreaks done by the inner console might
        # interfere with the outer console but there's no way to make the inner
        # console reactive so this is the best already.
        w, h = self.width, self.height = options.max_width, options.height
        texts = self.export_text(clear=False, styles=True).split("\n")
        texts = (Text.from_ansi(text) for text in texts[-h - 1 :])
        lines = itertools.chain.from_iterable(
            text.wrap(console, w, justify="left", tab_size=4) for text in texts
        )
        for line in list(lines)[-h - 1 :]:
            yield line


def main(args=None):
    rclpy.init(args=args)
    with Live(auto_refresh=False, screen=False) as live:
        node = MonitorNode(live)
        try:
            rclpy.spin(node)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
