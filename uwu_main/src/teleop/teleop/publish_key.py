import rclpy
from rclpy.node import Node
from std_msgs.msg import Char


class KeyPublisher(Node):

    def __init__(self):
        super().__init__('key_publisher')
        self.keypress_publisher = self.create_publisher(Char, '/keypress', 10)

    def log_keypress(self):
        while True:
            msg = Char()
            keypress = input("Enter a key: ")

            if len(keypress) > 1:
                self.get_logger().warn('Please enter a single character')
                continue

            msg.data = ord(keypress)
            self.keypress_publisher.publish(msg)
            self.get_logger().info('Publishing: "%s"' % keypress)

def main():
    rclpy.init()
    node = KeyPublisher()
    node.log_keypress()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()