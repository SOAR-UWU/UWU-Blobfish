import logging
import time
from datetime import datetime
from enum import IntEnum
from math import floor

import rclpy
import rclpy.qos
import textual.events as events
from geometry_msgs.msg import Twist
from rcl_interfaces.msg import Log
from rclpy.node import Node
from rclpy.time import Time
from rich.highlighter import ReprHighlighter
from rich.text import Text
from std_msgs.msg import Char, String
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import var
from textual.widgets import DataTable, Footer, Header, Label
from vectornav_msgs.msg import CommonGroup

from blobfish_msgs.msg import Kinematics, Motors, MotorsFloat

NODE_NAME = "monitor"
ROSOUT_LOG_LEVEL = logging.INFO
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

# TODO:
# - Use tabs to create other screens? https://textual.textualize.io/widgets/tabbed_content/
# - Sparklines for numerical data in another tab? https://textual.textualize.io/widgets/sparkline/


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

    CSS = """
    DataTable {
        height: 1fr;
        scrollbar-size: 1 1;
        overflow-y: scroll;
    }
    #kp_outer {
        width: 1fr;
    }
    #rosout_outer {
        width: 3fr;
    }
    Vertical > Label {
        width: 100%;
        height: 1;
        text-align: center;
    }
    """

    app_mode = var(AppMode.VIEW_ONLY, bindings=True)

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

        self.tables = {"kp": kp_table, "rosout": rosout_table}
        self.txt_highlighter = ReprHighlighter()

        yield Header(show_clock=True)
        with Horizontal():
            with Vertical(id="kp_outer"):
                yield Label("keypress log")
                yield kp_table
            with Vertical(id="rosout_outer"):
                yield Label("rosout log")
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

    # https://textual.textualize.io/events/mount/
    def on_mount(self) -> None:
        """Mount event handler."""
        self.write_kp_log("Press 'ctrl+m' till its 'KP Mode' to intercept keypresses.")
        self.refresh_datatable_sizes()

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
        # Assume the table is in a Vertical container.
        outer: Vertical = table.parent

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

        # TODO implement all default state w/o reactivity

        # Schedule ROS spin at 1000Hz.
        timer = self.set_interval(1e-3, lambda: rclpy.spin_once(node, timeout_sec=0))

        self.ros_node = node
        self.ros_timer = timer
        self.ros_kp_pub = kp_pub

    def ros_cb_imu_raw(self, msg: CommonGroup):
        pass

    def ros_cb_imu_cal(self, msg: Kinematics):
        pass

    def ros_cb_motor_order(self, msg: String):
        pass

    def ros_cb_motor_dbg(self, msg: MotorsFloat):
        pass

    def ros_cb_motor_real(self, msg: Motors):
        pass

    def ros_cb_pid(self, msg: Twist):
        pass

    def ros_cb_rosout(self, msg: Log):
        """Write rosout msgs to rosout_log."""
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
            (f"Sent: {event.character}")

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
