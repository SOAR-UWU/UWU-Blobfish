import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from motor_msg.msg import Motors, MotorOffset
import numpy as np
from std_msgs import char

class Direction_Control(Node):
    def __init__(self):
        super().__init__("motor_dir_control")

        self.motor_dir_control_publisher = self.create_publisher(MotorOffset, '/motor_dir_control', 10)
        self.order = ["bm", "fr", "br", "mr", "ml", "fl", "bl"]
        self.motor_values = []
        for name in self.order:
            self.declare_parameter(f"motor_{name}", 0)
            self.motor_values.append(self.get_parameter(name).value)
        self.motor_values = np.array(self.motor_values, dtype=np.float64)

        self.ws_state = None
        self.ID_value = 50
        self.create_subscription(char, '/keypress', self.keypress, 10)

        motor_msg = Motors()
        for i, name in enumerate(self.order):
            setattr(motor_msg, name, int(self.motor_values[i]))
        self.motor_dir_control_publisher.publish(motor_msg) 


    def check_dir_state(self, AD_key):
        if self.ws_state == 0: 
            
            if AD_key == "a":
                 self.motor_values[1]-=self.ID_value
                 self.motor_values[2]-=self.ID_value
                 self.motor_values[5]-=self.ID_value
                 self.motor_values[6]-=self.ID_value
                 self.get_logger().info("Decreased forward movement speed")

            elif AD_key == "d":
                self.motor_values[1]+=self.ID_value
                self.motor_values[2]+=self.ID_value
                self.motor_values[5]+=self.ID_value
                self.motor_values[6]+=self.ID_value
                self.get_logger().info("Increased forward movement speed")

        elif self.ws_state == 1:

            if AD_key == "a":
                self.motor_values[3]-=self.ID_value
                self.motor_values[4]-=self.ID_value
                self.get_logger().info("Decreased downward movement speed")
            
            elif AD_key == "d":
                self.motor_values[3]+=self.ID_value
                self.motor_values[4]+=self.ID_value
                self.get_logger().info("Increased downward movement speed")


    def keypress(self, msg):
        if msg.data == 'w': # Forward movement
            self.ws_state = 0
            self.get_logger().info("Entered forward movement state")
            self.check_dir_state(str(msg.data))
            # 1s timer?

        elif msg.data == 's': # Downward movement
            self.ws_state = 1
            self.get_logger().info("Entered downward movement state")
            self.check_dir_state(str(msg.data))
            # 1s timer?

        elif msg.data == 'a': # Decrease motor output
            if self.ws_state == 0 or 1:
                self.check_dir_state(str(msg.data))

        elif msg.data == 'd': # Increase motor output
            if self.ws_state == 0 or 1:
                self.check_dir_state(str(msg.data))

        else:
            self.ws_state = None
            self.get_logger().info("Invalid keypress")
        

def main():
    rclpy.init()
    node = Direction_Control()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
