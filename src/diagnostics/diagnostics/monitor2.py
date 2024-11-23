import logging
from enum import IntEnum

import rclpy
import rclpy.qos
import textual.events as events
from geometry_msgs.msg import Twist
from rcl_interfaces.msg import Log
from rclpy.node import Node
from rich.highlighter import ReprHighlighter
from rich.text import Text
from std_msgs.msg import Char, String
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.reactive import var
from textual.widgets import DataTable, Footer, Header
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

    app_mode = var(AppMode.VIEW_ONLY, bindings=True)

    def compose(self) -> ComposeResult:
        """Generator that yields the widgets to render."""
        kp_table = DataTable(fixed_columns=1, show_header=False, zebra_stripes=True)
        kp_table.add_column("Node", width=12)
        kp_col_msg = kp_table.columns[kp_table.add_column("Message", width=88)]

        self.txt_kp_table = kp_table
        self.txt_kp_col_msg = kp_col_msg
        self.txt_highlighter = ReprHighlighter()

        yield Header(show_clock=True)
        yield kp_table
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

    # https://textual.textualize.io/events/mount/
    def on_mount(self) -> None:
        """Mount event handler."""
        self.write_kp_log("Press 'ctrl+m' till its 'KP Mode' to intercept keypresses.")

    # https://textual.textualize.io/events/key/
    def on_key(self, event: events.Key) -> None:
        """Handle keypress events."""
        self.ros_pub_kp(event)

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
        pass

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

    def write_kp_log(self, msg: str, name="self", trim_rows=256):
        """Write a message to the kp_log."""
        # Don't show repeated names in consecutive rows.
        prev_name = getattr(self, "_prev_kp_name", None)
        if prev_name == name:
            name = ""
        else:
            self._prev_kp_name = name

        # NOTE: I can't find a way to dynamically wrap so we hardcode the width above.
        col_w = self.txt_kp_col_msg.width
        txt_name = Text(name, style="grey66", justify="right")
        lines = self.txt_highlighter(msg).wrap(None, col_w)
        self.txt_kp_table.add_row(txt_name, lines, height=len(lines))
        self.txt_kp_table.scroll_end(animate=False)

        keys = iter(self.txt_kp_table.rows)
        while self.txt_kp_table.row_count > trim_rows:
            self.txt_kp_table.remove_row(next(keys))


def main():
    """Main entry point for the application."""
    app = MonitorApp()
    app.run()


if __name__ == "__main__":
    main()
