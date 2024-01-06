import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from motor_msg.msg import Motors, MotorOffset
import numpy as np
from std_msgs import char

class Direction_Control(Node):
    def __init__(self):
        super().__init__("motor_dir_control_node")

        self.order = ["bm", "fr", "br", "mr", "ml", "fl", "bl"]
        self.motor_values = []
        for name in self.order:
            self.declare_parameter(f"motor_{name}", 0)
            self.motor_values.append(self.get_parameter(f"motor_{name}").value)

        self.fwd_motor_dir_values = [0, -1, 1, 0, 0, -1, 1]
        self.dwn_motor_dir_values = [0, 0, 0, 1, 1, 0, 0]
        
        self.ws_control_state = None
        self.inc_dec_value = 50

        self.motor_dir_control_publisher = self.create_publisher(MotorOffset, '/motor_dir_control', 10)
        self.create_subscription(char, '/keypress', self.keypress, 10)

        self.motor_values = np.array(self.motor_values, dtype=np.float64)

        motor_msg = Motors()
        for i, name in enumerate(self.order):
            setattr(motor_msg, name, int(self.motor_values[i]))
        self.motor_dir_control_publisher.publish(motor_msg) 


    def check_mov_state(self, AD_key_state):
        speed_change = self.inc_dec_value

        if self.ws_control_state == "move_forward_state": 
            for i in range(len(self.motor_values)):
                self.motor_values[i] *= self.fwd_motor_dir_values[i]

            if AD_key_state == "a":
                self.motor_values[1]-=speed_change
                self.motor_values[2]-=speed_change
                self.motor_values[5]-=speed_change
                self.motor_values[6]-=speed_change
                self.get_logger().info("Decreased forward movement speed:\n{self.motor_values}")

            elif AD_key_state == "d":
                self.motor_values[1]+=speed_change
                self.motor_values[2]+=speed_change
                self.motor_values[5]+=speed_change
                self.motor_values[6]+=speed_change
                self.get_logger().info("Increased forward movement speed:\n{self.motor_values}")

        elif self.ws_control_state == "move_downward_state":
            for i in range(len(self.motor_values)):
                self.motor_values[i] *= self.dwn_motor_dir_values[i]

            if AD_key_state == "a":
                self.motor_values[3]-=speed_change
                self.motor_values[4]-=speed_change
                self.get_logger().info("Decreased downward movement speed:\n{self.motor_values}")
            
            elif AD_key_state == "d":
                self.motor_values[3]+=speed_change
                self.motor_values[4]+=speed_change
                self.get_logger().info("Increased downward movement speed:\n{self.motor_values}")


    def keypress(self, msg):
        if msg.data == 'w':
            self.ws_control_state = "move_forward_state"
            self.get_logger().info("Entered forward movement state:\n{self.motor_values}")
            self.check_mov_state(str(msg.data))

        elif msg.data == 's': # Downward movement
            self.ws_control_state = "move_downward_state"
            self.get_logger().info("Entered downward movement state:\n{self.motor_values}")
            self.check_mov_state(str(msg.data))

        elif msg.data == 'a': # Decrease motor output
            if self.ws_control_state in ("move_forward_state", "move_downward_state"):
                self.check_mov_state(str(msg.data))

        elif msg.data == 'd': # Increase motor output
            if self.ws_control_state in ("move_forward_state", "move_downward_state"):
                self.check_mov_state(str(msg.data))

        else:
            self.ws_control_state = None
            self.get_logger().info("Invalid keypress")
        

def main():
    rclpy.init()
    node = Direction_Control()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
