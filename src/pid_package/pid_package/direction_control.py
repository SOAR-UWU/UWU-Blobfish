import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from motor_msg.msg import Motors, MotorOffset
import numpy as np
from std_msgs.msg import Char

class Direction_Control(Node):
    def __init__(self):
        super().__init__("motor_dir_control_node")

        self.motor_names = ["br", "bm", "fl", "fr", "ml", "bl", "mr"]
        self.motor_values = []
        for name in range(1, 8):
            self.declare_parameter(f"motor_{name}", 0)
            self.motor_values.append(self.get_parameter(f"motor_{name}").value)

        self.motor_order = dict()
        self.motor_directions = dict()
        for name in self.motor_names:
            self.declare_parameter(f"{name}_direction", 1)
            self.declare_parameter(f"{name}_order", 0)
            self.motor_order[name] = self.get_parameter(f"{name}_order").value
            self.motor_directions[name] = self.get_parameter(f"{name}_direction").value
        
        self.ws_control_state = None
        self.inc_dec_value = 20

        self.motor_dir_control_publisher = self.create_publisher(MotorOffset, '/motor_dir_control', 10)
        self.create_subscription(Char, '/keypress', self.keypress, 10)


    def check_mov_state(self, AD_key_state):

        if self.ws_control_state == "move_forward_state": 
            if AD_key_state == "q":
                self.motor_values[self.motor_order["fr"]]-=self.inc_dec_value*self.motor_directions["fr"]
                self.motor_values[self.motor_order["fl"]]-=self.inc_dec_value*self.motor_directions["fl"]
                self.motor_values[self.motor_order["br"]]-=self.inc_dec_value*self.motor_directions["br"]
                self.motor_values[self.motor_order["bl"]]-=self.inc_dec_value*self.motor_directions["bl"]
                self.get_logger().info(f"Decreased forward movement speed:\n{self.motor_values}")

            elif AD_key_state == "e":
                self.motor_values[self.motor_order["fr"]]+=self.inc_dec_value*self.motor_directions["fr"]
                self.motor_values[self.motor_order["fl"]]+=self.inc_dec_value*self.motor_directions["fl"]
                self.motor_values[self.motor_order["br"]]+=self.inc_dec_value*self.motor_directions["br"]
                self.motor_values[self.motor_order["bl"]]+=self.inc_dec_value*self.motor_directions["bl"]
                self.get_logger().info(f"Increased forward movement speed:\n{self.motor_values}")

        elif self.ws_control_state == "move_downward_state":
            speed_change = self.downward_dirs * self.inc_dec_value
            if AD_key_state == "q":
                self.motor_values[self.motor_order["ml"]]-=self.inc_dec_value*self.motor_directions["ml"]
                self.motor_values[self.motor_order["mr"]]-=self.inc_dec_value*self.motor_directions["mr"]
                self.get_logger().info(f"Decreased downward movement speed:\n{self.motor_values}")
            
            elif AD_key_state == "e":
                self.motor_values[self.motor_order["ml"]]+=self.inc_dec_value*self.motor_directions["ml"]
                self.motor_values[self.motor_order["mr"]]+=self.inc_dec_value*self.motor_directions["mr"]
                self.get_logger().info(f"Increased downward movement speed:\n{self.motor_values}")

        self.motor_values = np.array(self.motor_values, dtype=np.float64)
        motor_msg = MotorOffset()
        for i, name in enumerate(range(1, 8)):
            setattr(motor_msg, f"motor_{name}", int(self.motor_values[i]))
        self.motor_dir_control_publisher.publish(motor_msg) 


    def keypress(self, msg):
        key_data = chr(msg.data)

        if key_data == 'w':
            self.ws_control_state = "move_forward_state"
            self.get_logger().info(f"Entered forward movement state:\n{self.motor_values}")
            self.check_mov_state(key_data)

        elif key_data == 's': # Downward movement
            self.ws_control_state = "move_downward_state"
            self.get_logger().info(f"Entered downward movement state:\n{self.motor_values}")
            self.check_mov_state(key_data)

        elif key_data == 'q': # Decrease motor output
            if self.ws_control_state in ("move_forward_state", "move_downward_state"):
                self.check_mov_state(key_data)
            else:
                self.get_logger().info("Current movement state: None")

        elif key_data == 'e': # Increase motor output
            if self.ws_control_state in ("move_forward_state", "move_downward_state"):
                self.check_mov_state(key_data)
            else:
                self.get_logger().info("Current movement state: None")

        elif key_data == 'h':
            self.get_logger().info("Help:")
            self.get_logger().info("w - Tune forward values")
            self.get_logger().info("s - Tune downward values")
            self.get_logger().info("q - Decrease motor output")
            self.get_logger().info("e - Increase motor output")
            self.get_logger().info("Current movement state: " + str(self.ws_control_state))
        

def main():
    rclpy.init()
    node = Direction_Control()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
