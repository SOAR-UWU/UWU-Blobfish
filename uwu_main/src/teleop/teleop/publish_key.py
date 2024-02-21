import rclpy
from rclpy.node import Node
from std_msgs.msg import Char

import sys, termios, tty

class KeyPublisher(Node):

    def __init__(self):
        super().__init__('key_publisher')
        self.keypress_publisher = self.create_publisher(Char, '/keypress', 10)
        self.settings = termios.tcgetattr(sys.stdin)
        self.get_logger().info('Press a key to publish')

    def get_key(self):
        tty.setraw(sys.stdin.fileno())
        key = sys.stdin.read(1)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key

    def log_keypress(self):
        while True:
            msg = Char()
            keypress = self.get_key()

            if keypress == "\x03":
                break

            msg.data = ord(keypress)
            self.keypress_publisher.publish(msg)
            # self.get_logger().info('Publishing: "%s"' % keypress)

def main():
    rclpy.init()
    node = KeyPublisher()
    node.log_keypress()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()