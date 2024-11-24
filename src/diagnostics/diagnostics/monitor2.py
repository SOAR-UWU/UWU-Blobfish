"""Can RViz work over SSH? This is superior."""

import functools
import json
import time
from collections import defaultdict, deque
from datetime import datetime
from enum import IntEnum
from math import floor
from typing import Dict

import rclpy
import rclpy.qos
import textual.events as events
from geometry_msgs.msg import Point, Quaternion, Twist, Vector3
from rcl_interfaces.msg import Log
from rclpy.node import Node
from rclpy.time import Time
from rich.highlighter import ReprHighlighter
from rich.text import Text
from scipy.spatial.transform import Rotation
from std_msgs.msg import Char, String
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.reactive import var
from textual.widget import Widget
from textual.widgets import Collapsible, DataTable, Footer, Header, Label
from vectornav_msgs.msg import CommonGroup

from blobfish_msgs.msg import Kinematics, Motors, MotorsFloat

NODE_NAME = "monitor"
QOS = rclpy.qos.qos_profile_sensor_data

IMU_RAW_TOPIC = "/vectornav/raw/common"
IMU_CAL_TOPIC = "/blobfish/imu_measurements"
PID_TOPIC = "/blobfish/control_effort"
MOTOR_DEBUG_TOPIC = "/blobfish/motor_floats"
MOTOR_ACTUAL_TOPIC = "/blobfish/motor_values"
MOTOR_ORDER_TOPIC = "/blobfish/motor_order"
ROSOUT_TOPIC = "/rosout"
KEYPRESS_OUT_TOPIC = "/kpout"
KEYPRESS_TOPIC = "/keypress"


class AppMode(IntEnum):
    """Application modes."""

    KP = 0
    VIEW_ONLY = 1


ENUM_NAMES = {AppMode.KP: "KP Mode", AppMode.VIEW_ONLY: "View Mode"}
MODE_CYCLE_KEY = "ctrl+m"
COL_WIDTHS = {"name": 10, "time": 8}
COL_RESIZE_MIN_WIDTH = 32
DISPLAY_UPDATE_RATE = 4
MAX_VAL_BUF = 10

# TODO:
# - Use tabs to create other screens? https://textual.textualize.io/widgets/tabbed_content/
# - Sparklines for numerical data in another tab? https://textual.textualize.io/widgets/sparkline/
# - Table tooltips/select cell to copy.
# - Tooltips for widgets.
# - why aren't we using RViz/RQT?


class MonitorApp(App):
    """Frontend component for the ROS2 node."""

    # fmt: off
    # https://textual.textualize.io/guide/input/#bindings
    BINDINGS = [
        *[Binding(MODE_CYCLE_KEY, f"cycle_app_mode({m})", ENUM_NAMES[m], priority=True) for m in AppMode],
    ]
    # fmt: on
    TITLE = "J-H's Monitor"
    NOTIFICATION_TIMEOUT = 1
    CSS_PATH = "monitor2.tcss"

    app_mode = var(AppMode.VIEW_ONLY, bindings=True)

    # NOTE: Due to limitations, the tracked rate is multiple times lower than the actual rate.
    def rate_hz(name: str):
        """Decorator to calculate the frequency of a function call."""

        def decorator(callable):
            @functools.wraps(callable)
            def wrapper(self, *args, **kwargs):
                buf = self.__rate_buf[name]
                last = self.__rate_last[name]
                now = time.monotonic()
                buf.append(now - last)
                self.__rate_last[name] = now
                return callable(self, *args, **kwargs)

            return wrapper

        return decorator

    def compose(self) -> ComposeResult:
        """Generator that yields the widgets to render."""
        # We have code that dynamically resizes the columns of these tables.
        kp_table = DataTable(fixed_columns=1, show_header=False, zebra_stripes=True)
        kp_table.add_column("Node", width=1, key="name")
        kp_table.add_column("Message", width=1, key="msg")

        rosout_table = DataTable(fixed_columns=2, show_header=False, zebra_stripes=True)
        rosout_table.add_column("Node", width=1, key="name")
        rosout_table.add_column("Time", width=1, key="time")
        rosout_table.add_column("Message", width=1, key="msg")

        self.txt_highlighter = ReprHighlighter()
        self.tables = {"kp": kp_table, "rosout": rosout_table}
        # NOTE: Almost all names below are mapped to the ROS msg fields, change with caution.
        self.labels_rate = {
            k: Label(classes="stats") for k in ["imu_raw", "imu_cal", "motor", "pid"]
        }
        self.labels_imu_raw_rot = {k: Label(classes="stats") for k in ["r", "p", "h"]}
        self.labels_imu_raw_pos = {k: Label(classes="stats") for k in ["x", "y", "z"]}
        self.labels_imu_raw_acc = {
            k: Label(classes="stats") for k in ["ax", "ay", "az"]
        }
        self.labels_imu_cal_rot = {k: Label(classes="stats") for k in ["r", "p", "h"]}
        self.labels_imu_cal_pos = {k: Label(classes="stats") for k in ["x", "y", "z"]}
        self.labels_imu_cal_acc = {
            k: Label(classes="stats") for k in ["ax", "ay", "az"]
        }
        self.labels_pid = {
            k: Label(classes="stats") for k in ["r", "p", "h", "f", "l", "z"]
        }
        self.labels_motor_dbg = {
            k: Label(classes="stats")
            for k in ["FL", "FR", "ML", "MR", "BL", "BR", "BM"]
        }
        self.labels_motor_actual = {
            k: Label(classes="stats")
            for k in ["M1", "M2", "M3", "M4", "M5", "M6", "M7"]
        }

        yield Header(show_clock=True)
        with Horizontal():
            for v in self.labels_rate.values():
                yield v
        with Horizontal():
            with Collapsible(title="Raw IMU", collapsed=False):
                with Container(classes="grid33"):
                    for v in self.labels_imu_raw_rot.values():
                        yield v
                    for v in self.labels_imu_raw_pos.values():
                        yield v
                    for v in self.labels_imu_raw_acc.values():
                        yield v
            with Collapsible(title="Calibrated IMU", collapsed=False):
                with Container(classes="grid33"):
                    for v in self.labels_imu_cal_rot.values():
                        yield v
                    for v in self.labels_imu_cal_pos.values():
                        yield v
                    for v in self.labels_imu_cal_acc.values():
                        yield v
        with Collapsible(title="Motor Signals", collapsed=False):
            with Container(classes="grid73"):
                for v in self.labels_pid.values():
                    yield v
                # Extra label to fill space.
                yield Label(classes="stats")
                for v in self.labels_motor_dbg.values():
                    yield v
                for v in self.labels_motor_actual.values():
                    yield v
        with Horizontal(id="log_outer"):
            with Collapsible(id="kp_outer", title="Keypress Log", collapsed=False):
                yield kp_table
            with Collapsible(id="rosout_outer", title="Rosout Log", collapsed=False):
                yield rosout_table
        yield Footer()

    # https://textual.textualize.io/guide/actions/
    def action_cycle_app_mode(self, prev: int) -> None:
        """Cycle app mode."""
        self.app_mode = AppMode((prev + 1) % len(AppMode))

    # https://textual.textualize.io/guide/actions/#dynamic-actions
    def check_action(self, action: str, args: tuple):
        """Check if action should be enabled."""
        if action == "cycle_app_mode":
            return self.app_mode == AppMode(args[0])
        return True

    # https://textual.textualize.io/events/load/
    def on_load(self) -> None:
        """Load event handler."""
        self.ros_init()

        self.__prev_table_row_val = {}
        self.__rate_buf = defaultdict(lambda: deque(maxlen=MAX_VAL_BUF))
        self.__rate_last = defaultdict(int)

    # https://textual.textualize.io/events/mount/
    def on_mount(self) -> None:
        """Mount event handler."""
        self.write_kp_log("Press 'ctrl+m' till its 'KP Mode' to intercept keypresses.")
        self.refresh_datatable_sizes()
        self.set_interval(1.0 / DISPLAY_UPDATE_RATE, self.update_display)

    # https://textual.textualize.io/events/key/
    def on_key(self, event: events.Key) -> None:
        """Handle keypress events."""
        self.ros_pub_kp(event)

    # https://textual.textualize.io/events/resize/
    def on_resize(self, event: events.Resize) -> None:
        """Handle resize events."""
        self.refresh_datatable_sizes()

    def refresh_datatable_sizes(self):
        """Refresh sizes of all data tables."""
        for table in self.tables.values():
            table.call_after_refresh(self.handle_table_resize, table)

    def handle_table_resize(self, table: DataTable, col_to_resize="msg"):
        """Resize table's msg column to fit."""
        outer: Widget = table.parent

        w = outer.size.width - 2 * table.cell_padding - table.scrollbar_size_vertical
        ew = 0
        for k, col in table.columns.items():
            colw = COL_WIDTHS.get(k, 0)
            if colw > 0:
                w -= colw + 2 * table.cell_padding
                # If later w < COL_RESIZE_MIN_WIDTH, all other cols are set to 1.
                ew += colw - 1
                col.width = colw

        if w >= COL_RESIZE_MIN_WIDTH:
            table.columns[col_to_resize].width = w
        else:
            for col in table.columns.values():
                col.width = 1
            table.columns[col_to_resize].width = max(w + ew, 1)

        # Force row height to update.
        rows = list(table.rows.keys())
        for r in rows:
            table.rows[r].height = 0
        table._update_dimensions(rows)
        table.call_after_refresh(table.scroll_end, animate=False)

    def watch_app_mode(self, mode: AppMode):
        """Watch app mode changes."""
        if mode == AppMode.KP:
            self.notify("Intercept all keypresses: True")
        else:
            self.notify("Intercept all keypresses: False")

    def ros_init(self):
        """Initialize ROS stuff."""
        rclpy.init()

        node = Node(NODE_NAME)

        # fmt: off
        node.create_subscription(CommonGroup, IMU_RAW_TOPIC, self.ros_cb_imu_raw, QOS)
        node.create_subscription(Kinematics, IMU_CAL_TOPIC, self.ros_cb_imu_cal, QOS)
        node.create_subscription(String, MOTOR_ORDER_TOPIC, self.ros_cb_motor_order, 10)
        node.create_subscription(MotorsFloat, MOTOR_DEBUG_TOPIC, self.ros_cb_motor_dbg, QOS)
        node.create_subscription(Motors, MOTOR_ACTUAL_TOPIC, self.ros_cb_motor_real, QOS)
        node.create_subscription(Twist, PID_TOPIC, self.ros_cb_pid, QOS)
        node.create_subscription(Log, ROSOUT_TOPIC, self.ros_cb_rosout, 10)
        node.create_subscription(Log, KEYPRESS_OUT_TOPIC, self.ros_cb_kp_out, 10)
        kp_pub = node.create_publisher(Char, KEYPRESS_TOPIC, 10)
        # fmt: on

        async def spin_task():
            def spin():
                while self.is_running:
                    rclpy.spin_once(node, timeout_sec=0)

            await self._loop.run_in_executor(None, spin)

        self._loop.create_task(spin_task())
        # self.set_interval(1.0 / ROS_UPDATE_RATE, lambda: rclpy.spin_once(node, timeout_sec=0))

        self.ros_node = node
        self.ros_kp_pub = kp_pub
        self.ros_imu_raw = CommonGroup()
        self.ros_imu_cal = Kinematics()
        self.ros_motor_order = None
        self.ros_motor_dbg = MotorsFloat()
        self.ros_motor_actual = Motors()
        self.ros_pid = Twist()
        self.buf_imu_raw_acc = {k: deque(maxlen=MAX_VAL_BUF) for k in ["x", "y", "z"]}
        self.buf_imu_cal_acc = {k: deque(maxlen=MAX_VAL_BUF) for k in ["x", "y", "z"]}

    @rate_hz("imu_raw")
    def ros_cb_imu_raw(self, msg: CommonGroup):
        state = self.ros_imu_raw
        state.quaternion = msg.quaternion
        state.position = msg.position
        # Get max acceleration within buffer.
        for k, buf in self.buf_imu_raw_acc.items():
            buf.append(getattr(msg.accel, k))
            setattr(state.accel, k, max(buf, key=abs))

    @rate_hz("imu_cal")
    def ros_cb_imu_cal(self, msg: Kinematics):
        state = self.ros_imu_cal
        state.p.orientation = msg.p.orientation
        state.p.position = msg.p.position
        # Get max acceleration within buffer.
        for k, buf in self.buf_imu_cal_acc.items():
            buf.append(getattr(msg.a.linear, k))
            setattr(state.a.linear, k, max(buf, key=abs))

    def ros_cb_motor_order(self, msg: String):
        try:
            order = json.loads(msg.data)
            self.ros_motor_order = {v: k for k, v in order.items()}
        except json.JSONDecodeError:
            self.ros_motor_order = None
            self.ros_node.get_logger().error(
                f"Failed to parse motor order JSON: {msg.data}"
            )

    def ros_cb_motor_dbg(self, msg: MotorsFloat):
        self.ros_motor_dbg = msg

    @rate_hz("motor")
    def ros_cb_motor_real(self, msg: Motors):
        self.ros_motor_actual = msg

    @rate_hz("pid")
    def ros_cb_pid(self, msg: Twist):
        self.ros_pid = msg

    def ros_cb_rosout(self, msg: Log):
        """Write rosout msgs to rosout_log."""
        # TODO: how to map original file location? Use a Link widget?
        # msg.stamp, msg.level, msg.name, msg.msg, msg.file, msg.function, msg.line
        time = Time.from_msg(msg.stamp)
        s, _ = time.seconds_nanoseconds()
        self.write_rosout_log(msg.msg, name=msg.name, ts=s)

    def ros_cb_kp_out(self, msg: Log):
        """Write keypress msgs to kp_log."""
        self.write_kp_log(msg.msg, name=msg.name)

    def ros_pub_kp(self, event: events.Key):
        """Publish a keypress."""
        if not self.app_mode == AppMode.KP:
            return
        event.prevent_default()
        if event.character is not None:
            msg = Char()
            msg.data = ord(event.character)
            self.ros_kp_pub.publish(msg)
            self.write_kp_log(f"Sent: '{event.character}'")

    def update_display_rate(self):
        """Update rate labels."""
        lbls = self.labels_rate
        for k, lbl in lbls.items():
            buf = self.__rate_buf[k]
            fps = 0.0
            if len(buf) > 0:
                fps = 1.0 / max(sum(buf) / len(buf), 1e-6)
                # Allow stale rate values to be removed.
                buf.popleft()
            lbl.update(f"{k}: [bold bright_cyan]{fps: 5.1f}[/bold bright_cyan] Hz")

    def update_display_imu_rot(self, lbls: Dict[str, Label], q: Quaternion):
        """Update imu rotation labels."""
        rot = Rotation.from_quat((q.x, q.y, q.z, q.w)).as_euler("xyz", degrees=True)
        for i, (k, lbl) in enumerate(lbls.items()):
            lbl.update(f"{k: >2}: [bold bright_cyan]{rot[i]: 8.1f}")

    def update_display_imu_pos(self, lbls: Dict[str, Label], p: Point):
        """Update imu position labels."""
        for k, lbl in lbls.items():
            lbl.update(f"{k: >2}: [bold bright_cyan]{getattr(p, k): 8.3f}")

    def update_display_imu_acc(self, lbls: Dict[str, Label], a: Vector3):
        for k, lbl in lbls.items():
            lbl.update(f"{k: >2}: [bold bright_cyan]{getattr(a, k[1]): 8.3f}")

    def update_display_pid(self):
        """Update pid labels."""
        ang = self.ros_pid.angular
        lin = self.ros_pid.linear

        self.labels_pid["r"].update(f"{'r': >6}: [bold bright_cyan]{ang.x: 6.3f}")
        self.labels_pid["p"].update(f"{'p': >6}: [bold bright_cyan]{ang.y: 6.3f}")
        self.labels_pid["h"].update(f"{'h': >6}: [bold bright_cyan]{ang.z: 6.3f}")
        self.labels_pid["f"].update(f"{'f': >6}: [bold bright_cyan]{lin.x: 6.3f}")
        self.labels_pid["l"].update(f"{'l': >6}: [bold bright_cyan]{lin.y: 6.3f}")
        self.labels_pid["z"].update(f"{'z': >6}: [bold bright_cyan]{lin.z: 6.3f}")

    def update_display_motor_dbg(self):
        """Update motor debug labels."""
        for k, lbl in self.labels_motor_dbg.items():
            m = getattr(self.ros_motor_dbg, k.lower())
            lbl.update(f"{k: >6}: [bold bright_cyan]{m: 6.3f}")

    def update_display_motor_actual(self):
        """Update motor actual labels."""
        N = 7
        order = self.ros_motor_order
        lbls = self.labels_motor_actual
        for i in range(1, N + 1):
            k = f"M{i}"
            o = "" if order is None else f"({order[i-1].upper()})"
            n = f"{o}{k}"
            v = getattr(self.ros_motor_actual, f"motor_{i}")
            lbls[k].update(f"{n: >6}:  [bold bright_cyan]{v:04d}")

    def update_display(self):
        """Update display with new data."""
        self.update_display_rate()
        self.update_display_imu_rot(
            self.labels_imu_raw_rot, self.ros_imu_raw.quaternion
        )
        self.update_display_imu_pos(self.labels_imu_raw_pos, self.ros_imu_raw.position)
        self.update_display_imu_acc(self.labels_imu_raw_acc, self.ros_imu_raw.accel)

        self.update_display_imu_rot(
            self.labels_imu_cal_rot, self.ros_imu_cal.p.orientation
        )
        self.update_display_imu_pos(
            self.labels_imu_cal_pos, self.ros_imu_cal.p.position
        )
        self.update_display_imu_acc(self.labels_imu_cal_acc, self.ros_imu_cal.a.linear)
        self.update_display_pid()
        self.update_display_motor_dbg()
        self.update_display_motor_actual()

    def write_datatable(
        self,
        table_name: str,
        msg: str,
        name: str,
        ts: int,
        has_ts: bool,
        trim_rows: int,
    ):
        """Write a log message to a datatable."""
        prev_name = self.__prev_table_row_val.get(f"{table_name}_name", "")
        prev_ts = self.__prev_table_row_val.get(f"{table_name}_ts", -1)

        # Don't show repeated name/time in consecutive rows.
        if prev_name == name and prev_ts == ts:
            name = ""
            ts = -1
        else:
            self.__prev_table_row_val[f"{table_name}_name"] = name
            self.__prev_table_row_val[f"{table_name}_ts"] = ts

        time_str = (
            str(datetime.fromtimestamp(ts).strftime("%H:%M:%S")) if ts != -1 else ""
        )

        txt_name = Text(
            name, style="grey66", justify="right", no_wrap=True, overflow="ellipsis"
        )
        txt_time = Text(
            time_str, style="grey66", justify="right", no_wrap=True, overflow="ellipsis"
        )
        txt_msg = self.txt_highlighter(msg)

        table = self.tables[table_name]
        if has_ts:  # height=None enables auto height
            table.add_row(txt_name, txt_time, txt_msg, height=None)
        else:
            table.add_row(txt_name, txt_msg, height=None)

        # Remove oldest rows if needed.
        keys = iter(table.rows)
        while table.row_count > trim_rows:
            table.remove_row(next(keys))

        # Scroll only if at the bottom.
        if abs(table.scroll_y - table.max_scroll_y) < 5:
            table.scroll_end(animate=False)

    def write_kp_log(self, msg: str, name="self", trim_rows=256):
        """Write a message to the kp log."""
        self.write_datatable("kp", msg, name, -1, False, trim_rows)

    def write_rosout_log(self, msg: str, name="self", ts=None, trim_rows=1024):
        """Write a message to the rosout log."""
        if ts is None:
            ts = time.time()

        self.write_datatable("rosout", msg, name, int(floor(ts)), True, trim_rows)


def main():
    """Main entry point for the application."""
    app = MonitorApp()
    app.run()


if __name__ == "__main__":
    main()
