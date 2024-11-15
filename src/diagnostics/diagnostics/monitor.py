"""Yeah, this isn't a generic topic monitor yet, it just monitors motor & IMU really well.

Say why aren't we using RViz?
"""

import itertools
import json
import logging
import os
from collections import defaultdict, deque

import getchlib
import rclpy
import rclpy.qos
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
MOTOR_DEBUG_TOPIC = "/blobfish/motor_floats"
MOTOR_ACTUAL_TOPIC = "/blobfish/motor_values"
MOTOR_ORDER_TOPIC = "/blobfish/motor_order"
ROSOUT_TOPIC = "/rosout"
KEYPRESS_OUT_TOPIC = "/kpout"
KEYPRESS_TOPIC = "/keypress"

QOS = rclpy.qos.qos_profile_sensor_data
ROSOUT_LOG_LEVEL = logging.INFO
RATE = 30

# TODO:
# - why aren't we using RViz/RQT?
# - OG keypress node should use keypress out too
# - tmux shell scripts for sim, irl & sim-irl testing
# - Put rate monitors into panel title for each msg type


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
        self.create_subscription(
            String, MOTOR_ORDER_TOPIC, self.motor_order_callback, 10
        )
        self.create_subscription(Log, ROSOUT_TOPIC, self.rosout_callback, 10)
        self.create_subscription(
            Log, KEYPRESS_OUT_TOPIC, self.keypress_out_callback, 10
        )
        self.create_timer(1 / RATE, self.key_timer_callback)

        self.__key_pub = self.create_publisher(Char, KEYPRESS_TOPIC, 10)
        self.create_layout(live)

    def create_layout(self, live: Live):
        L = Layout()
        rosout = ConsolePanel()
        kpout = ConsolePanel()
        imu_raw = Panel("no data yet", title="VN-100")
        imu_cal = Panel("no data yet", title="Calibrated")
        motors = Panel("no data yet", title="Motors")

        L.split_column(
            Layout(name="imu", size=5),
            Layout(motors, name="motor", size=4),
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
        self.__layout = L
        self.__panel_imu_raw = imu_raw
        self.__panel_imu_cal = imu_cal
        self.__panel_motors = motors
        self.__rate_buf = defaultdict(lambda: deque(maxlen=10))
        self.__rate_last = defaultdict(int)
        self.__motor_order = None
        self.__motor_debug_str = ""
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

    def imu_raw_callback(self, msg: CommonGroup):
        ypr = msg.yawpitchroll
        pos = msg.position  # Depending on how we decide to do the integrator
        acc = msg.accel
        self.__panel_imu_raw.renderable = Text(
            f" r: {ypr.z: 8.1f}\t p: {ypr.y: 8.1f}\t h: {ypr.x: 8.1f}\n"
            f" x: {pos.x: 8.3f}\t y: {pos.y: 8.3f}\t z: {pos.z: 8.3f}\n"
            f"ax: {acc.x: 8.3f}\tay: {acc.y: 8.3f}\taz: {acc.z: 8.3f}"
        )
        # TODO: Rate measurement can't keep up
        # last = self.__rate_last["imu_raw"]
        # now = time.time()
        # self.__rate_buf["imu_raw"].append(now - last)
        # self.__rate_last["imu_raw"] = now
        # fps = 1 / max(1e-8, np.mean(self.__rate_buf["imu_raw"]))
        # self.__panel_imu_raw.subtitle = f"{fps: 5.1f} Hz"

    def imu_cal_callback(self, msg: Kinematics):
        pos = msg.p.position
        acc = msg.a.linear
        quat = msg.p.orientation
        rot = Rotation.from_quat((quat.x, quat.y, quat.z, quat.w))
        r, p, h = rot.as_euler("xyz", degrees=True)
        self.__panel_imu_cal.renderable = Text(
            f" r: {r: 8.1f}\t p: {p: 8.1f}\t h: {h: 8.1f}\n"
            f" x: {pos.x: 8.3f}\t y: {pos.y: 8.3f}\t z: {pos.z: 8.3f}\n"
            f"ax: {acc.x: 8.3f}\tay: {acc.y: 8.3f}\taz: {acc.z: 8.3f}"
        )

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

    def motor_actual_callback(self, msg: Motors):
        N = 7
        if self.__motor_order is None:
            pairs = {f"motor_{i}": getattr(msg, f"motor_{i}") for i in range(1, N + 1)}
        else:
            pairs = {
                f"motor_{i} ({self.__motor_order[i - 1].upper()})": getattr(
                    msg, f"motor_{i}"
                )
                for i in range(1, N + 1)
            }
        self.__panel_motors.renderable = Text(
            self.__motor_debug_str
            + "\t".join((f"{k}: {v:04d}" for k, v in pairs.items()))
        )

    def motor_order_callback(self, msg: String):
        try:
            order = json.loads(msg.data)
            self.__motor_order = {v: k for k, v in order.items()}
        except json.JSONDecodeError:
            self.get_logger().error("Invalid JSON in motor order")
            self.__motor_order = None

    def rosout_callback(self, msg: Log):
        # TODO: how to map original time & file location to Rich logging?
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

    def key_timer_callback(self):
        key = self.get_key()
        if key is not None:
            for k in key:
                msg = Char()
                msg.data = ord(k)
                self.__key_pub.publish(msg)

    def get_key(self):
        ch: str = getchlib.getkey(False, echo=False)
        return None if ch == "" else ch


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
    with Live(refresh_per_second=RATE, screen=True) as live:
        node = MonitorNode(live)
        try:
            rclpy.spin(node)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
