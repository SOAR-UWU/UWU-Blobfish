from typing import Optional

import python_qt_binding
import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import Int32

from .base_bridge import create_bridge

GZ_TOPIC = "/gz/keyboard/keypress"
GAME_TOPIC = "/blobfish/game_setpoint"
LIN_MAG = 0.2
ROT_MAG = 0.4


def map_keypress(msg: Int32, node: Node) -> Optional[Twist]:
    """Parse qt keycode to char and publish."""
    # TODO: Gazebo triggers keypress twice since their plugin doesn't filter key up vs key down.
    # I am seriously considering copying their keypress plugin and fixing it myself.
    log = node.get_logger()
    qtcode = msg.data
    typed: str = ""

    try:
        qtkeyseq = python_qt_binding.QtGui.QKeySequence(qtcode)
        typed = qtkeyseq.toString()
        log.debug(f"Received qt keycode: {typed}")
    except Exception as e:
        log.debug(f"Failed to parse qt keycode ({qtcode}): {e}")
        return

    if len(typed) == 1:
        typed = typed.lower()
    # Shift + Space works.
    elif typed.lower() == "space":
        typed = " "
    # Handling only alphanumerics, discard others.
    elif len(typed) > 1:
        typed = None

    if typed:
        out = Twist()
        # rotate anti-clockwise
        if typed in "aA":
            out.angular.z = ROT_MAG
            return out
        # rotate clockwise
        elif typed in "dD":
            out.angular.z = -ROT_MAG
            return out
        # move forward
        elif typed in "wW":
            out.linear.x = LIN_MAG
            return out
        # move backward
        elif typed in "sS":
            out.linear.x = -LIN_MAG
            return out
        # move up
        elif typed in "eE":
            out.linear.z = LIN_MAG * 2
            return out
        # move down
        elif typed in "qQ":
            out.linear.z = -LIN_MAG * 2
            return out
        # roll left
        elif typed in "zZ":
            out.angular.x = -ROT_MAG
            return out
        # roll right
        elif typed in "cC":
            out.angular.x = ROT_MAG
            return out


def main(args=None):
    rclpy.init(args=args)
    node = create_bridge(
        map_keypress, GZ_TOPIC, Int32, GAME_TOPIC, Twist, from_profile=10
    )
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
