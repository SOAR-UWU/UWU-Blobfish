import rclpy
from rclpy.node import Node
from std_msgs import Char

class PID_Tuner(Node):

    def __init__(self):
        super().__init__('pid_tuner')
        self.keypress_sub = self.create_subscription(
            Char, "/keypress", self.proc_keypress, 10)
        self.get_logger().info("PID Tuner node started")
        self.current_variable = None
        self.current_axis = None
        
    def proc_keypress(self, msg):
        keypress = chr(msg.data)
        if self.current_variable == None:
            if keypress in "pP":
                self.current_variable = "p"
                self.get_logger().info("Tuning P")
            if keypress in "iI":
                self.current_variable = "i"
                self.get_logger().info("Tuning I")
            if keypress in "dD":
                self.current_variable = "d"
                self.get_logger().info("Tuning D")

def main():
    rclpy.init()
    node = PID_Tuner()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
        
        