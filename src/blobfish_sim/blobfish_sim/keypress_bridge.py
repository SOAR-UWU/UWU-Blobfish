"""Node that converts Gazebo's keypress topic to ours.

`blobfish_control/publish_key.py` uses Python's `chr()` & `ord()` for keypresses.
This notably doesn't support arrow keys as a single character. Lowercase, uppercase,
and some key combos (ctrl + key) are supported.

In contrast, Gazebo's keypress publisher uses Qt::Key event codes. See:
- Implementation: https://github.com/gazebosim/gz-gui/blob/gz-gui9/src/plugins/key_publisher/KeyPublisher.cc
- Qt docs for function: https://doc.qt.io/qt-6/qkeyevent.html#key
- Qt key codes: https://doc.qt.io/qt-6/qt.html#Key-enum
Unfortunately, the function used in KeyPublisher.cc doesn't support uppercase & defaults to uppercase.

Below, I aim to support `chr()` primarily for ease of all other ROS2 nodes. However,
that means arrow keys aren't supported.

Also, I give up, and we only support lowercase alphanumeric keys in simulation now.

Oh this is cursed ROS created its own Python bindings for Qt: https://wiki.ros.org/python_qt_binding
"""

import python_qt_binding
import rclpy
from rclpy.node import Node
from std_msgs.msg import Char, Int32

NODE_NAME = "gz_keypress_bridge"
GZ_TOPIC = "/gz/keyboard/keypress"
KEYPRESS_TOPIC = "/keypress"


class KeypressBridgeNode(Node):
    def __init__(self):
        super(KeypressBridgeNode, self).__init__(NODE_NAME)

        self.create_subscription(Int32, GZ_TOPIC, self.keypress_callback, 10)
        self.pub_keypress = self.create_publisher(Char, KEYPRESS_TOPIC, 10)

    def keypress_callback(self, msg: Int32):
        """Parse qt keycode to char and publish."""
        qtcode = msg.data
        typed = None
        try:
            qtkeyseq = python_qt_binding.QtGui.QKeySequence(qtcode)
            typed = qtkeyseq.toString()
            self._logger.debug(f"Received qt keycode: {typed}")
        except Exception as e:
            self._logger.debug(f"Failed to parse qt keycode ({qtcode}): {e}")
            return

        if len(typed) == 1:
            typed = ord(typed[0].lower())
        # Shift + Space works.
        elif typed.lower() == "space":
            typed = ord(" ")
        # Handling only alphanumerics, discard others.
        elif len(typed) > 1:
            typed = None

        if typed is not None:
            self.pub_keypress.publish(Char(data=typed))


def main():
    rclpy.init()
    node = KeypressBridgeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.close()
        node.destroy_node()


if __name__ == "__main__":
    main()
