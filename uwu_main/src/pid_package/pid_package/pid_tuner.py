import rclpy
from rclpy.node import Node
from std_msgs.msg import Char

class PID_Tuner(Node):

    def __init__(self):
        super().__init__('pid_tuner')
        self.keypress_sub = self.create_subscription(
            Char, "/keypress", self.proc_keypress, 10)
        self.get_logger().info("PID Tuner node started")
        self.current_variable = None
        self.current_axis = None
        self.unit = 0.003
        
    def proc_keypress(self, msg):
        keypress = chr(msg.data)
        if keypress in "pP":
            self.current_variable = "p"
            self.get_logger().info("Tuning P")
        if keypress in "iI":
            self.current_variable = "i"
            self.get_logger().info("Tuning I")
        if keypress in "dD":
            self.current_variable = "d"
            self.get_logger().info("Tuning D")
        if keypress in "rR":
            self.current_axis = "roll"
            self.get_logger().info("Tuning roll")
        if keypress in "hH":
            self.current_axis = "pitch"
            self.get_logger().info("Tuning pitch")
        if keypress in "yY":
            self.current_axis = "yaw"
            self.get_logger().info("Tuning yaw")
        
        if self.current_axis != None and self.current_variable != None:
            if keypress in ",.":
                param_name = f"k{self.current_variable}_{self.current_axis}"
                param_val = self.get_parameter(param_name).value

            if keypress == ",":
                param_val -= self.unit
                new_param = rclpy.parameter.Parameter(
                    param_name,
                    rclpy.Parameter.Type.DOUBLE,
                    param_val
                )
                self.get_logger().info(f"Decreasing {param_name} to {param_val}")
                self.set_parameters([new_param])
            if keypress == ".":
                param_val += self.unit
                new_param = rclpy.parameter.Parameter(
                    param_name,
                    rclpy.Parameter.Type.DOUBLE,
                    param_val
                )
                self.get_logger().info(f"Increasing {self.current_variable} of {self.current_axis}")

def main():
    rclpy.init()
    node = PID_Tuner()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
        
        