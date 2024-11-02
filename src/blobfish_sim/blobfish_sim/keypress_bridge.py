"""Node that converts Gazebo's sensor topics to ours, remapping & transforming values to IRL ranges if needed."""

from typing import Optional

import python_qt_binding
import rclpy
from rclpy.node import Node
from std_msgs.msg import Char, Int32

from .base_bridge import create_bridge_node

G_KEYPRESS_TOPIC = "/gz/keyboard/keypress"
R_KEYPRESS_TOPIC = "/keypress"


def map_keypress(msg: Int32, node: Node) -> Optional[Char]:
    """Parse qt keycode to char and publish."""
    # TODO: Gazebo triggers keypress twice since their plugin doesn't filter key up vs key down.
    # I am seriously considering copying their keypress plugin and fixing it myself.
    log = node.get_logger()
    qtcode = msg.data
    typed: str = ""
    pycode: Optional[int] = None

    try:
        qtkeyseq = python_qt_binding.QtGui.QKeySequence(qtcode)
        typed = qtkeyseq.toString()
        log.debug(f"Received qt keycode: {typed}")
    except Exception as e:
        log.debug(f"Failed to parse qt keycode ({qtcode}): {e}")
        return

    if len(typed) == 1:
        pycode = ord(typed.lower())
    # Shift + Space works.
    elif typed.lower() == "space":
        pycode = ord(" ")
    # Handling only alphanumerics, discard others.
    elif len(typed) > 1:
        pycode = None

    if pycode is not None:
        return Char(data=pycode)


def main(args=None):
    try:
        rclpy.init(args=args)
        node = create_bridge_node(
            map_keypress, G_KEYPRESS_TOPIC, Int32, R_KEYPRESS_TOPIC, Char
        )
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
