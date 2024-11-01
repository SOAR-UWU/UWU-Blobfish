"""Node that converts Gazebo's sensor topics to ours, remapping & transforming values to IRL ranges if needed."""

import python_qt_binding
import rclpy
from rclpy.node import Node
from std_msgs.msg import Char, Int32

NODE_NAME = "blobfish_sim_bridge"
G_KEYPRESS_TOPIC = "/gz/keyboard/keypress"
R_KEYPRESS_TOPIC = "/keypress"
G_IMU_TOPIC = "/gz/blobfish/imu"
R_IMU_TOPIC = "/blobfish/imu_measurements"


class SimBridgeNode(Node):
    def __init__(self):
        super(SimBridgeNode, self).__init__(NODE_NAME)

        self.create_subscription(Int32, G_KEYPRESS_TOPIC, self.keypress_callback, 10)
        self.pub_keypress = self.create_publisher(Char, R_KEYPRESS_TOPIC, 10)

    def keypress_callback(self, msg: Int32):
        """Parse qt keycode to char and publish."""
        # TODO: Gazebo triggers keypress twice since their plugin doesn't filter key up vs key down.
        # I am seriously considering copying their keypress plugin and fixing it myself.
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
    node = SimBridgeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()


if __name__ == "__main__":
    main()
