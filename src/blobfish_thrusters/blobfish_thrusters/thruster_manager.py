import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Char
from blobfish_msgs.msg import Motors, MotorOffset
import numpy as np
from rclpy.parameter import Parameter

class Thruster_Manager(Node):
    def __init__(self):
        super().__init__("thruster_manager")
        
        # The following section reads the motor positions and directions from the
        # parameter server and orders the motors in the correct order in the matrix.
        # The ROS param <motor_name>_order should be a number from 1 to 7, denoting
        # the number of that motor based on the motor_msg.
        motor_vector_collection = {
            # r p h x y z 
            "br": [0,   0,  -1,  1,     -1,   0],
            "bm": [0,   1,  0,  0,     0,    0],
            "fl": [0,   0,  -1,  -1,    1,    0],
            "fr": [0,    0, 1,  -1,    -1,    0],
            "ml": [-1,  0,  0,  0,     0,    1],
            "bl": [0,   0,  1,  1,     1,    0],
            "mr": [1,   0,  0,  0,     0,    1]
        }

        # Check the config file for the actual values of these parameters
        
        # Order, meaning the mapping from motor position to motor number on Arduino.
        self.declare_parameter("br_order", Parameter.Type.INTEGER)
        self.declare_parameter("bm_order", Parameter.Type.INTEGER)
        self.declare_parameter("fl_order", Parameter.Type.INTEGER)
        self.declare_parameter("fr_order", Parameter.Type.INTEGER)
        self.declare_parameter("ml_order", Parameter.Type.INTEGER)
        self.declare_parameter("bl_order", Parameter.Type.INTEGER)
        self.declare_parameter("mr_order", Parameter.Type.INTEGER)

        # Get the values of the declared parameters
        self.motor_names = [f"motor_{num}" for num in range(1, 8)]
        self.motors = ["br", "bm", "fl", "fr", "ml", "bl", "mr"]
        
        motor_orders = []
        for motor_name, motor_vector in motor_vector_collection.items():
            motor_vector = np.array(motor_vector)
            motor_pos = self.get_parameter(f"{motor_name}_order")
            motor_orders.append((motor_pos.value, motor_vector))

        motor_orders.sort(key=lambda x: x[0])

        arr = [motor[1] for motor in motor_orders]

        self.motor_matrix = np.array(arr, dtype=np.float64)

        self.scale = 300    # how much to scale the pid value
        self.create_subscription(Twist, 'blobfish/control_effort', self.calculate_thrusters, 10)
        self.create_subscription(Char, 'keypress', self.toggle_motors, 10)
        self.motor_publisher = self.create_publisher(Motors, 'blobfish/motor_values', 10)
        self.get_logger().info("Thruster manager started")
        self.stopped = False

    def toggle_motors(self, msg):
        keypress = chr(msg.data)
        if keypress == " ":
            self.stopped = not self.stopped
            self.get_logger().info(f"Motors running: {not self.stopped}")
        elif keypress == "h":
            self.get_logger().info("Press SPACE to turn off/on the motors")
    
    def calculate_thrusters(self, pid_msg):
        if self.stopped:
            motor_vals = Motors()
            for i, name in enumerate(self.motor_names):
                setattr(motor_vals, name, 1500)
            self.motor_publisher.publish(motor_vals)
            return
            
        pid_weights = np.array([
            [pid_msg.angular.x],    # roll
            [pid_msg.angular.y],    # pitch
            [pid_msg.angular.z],    # yaw
            [pid_msg.linear.x],     # forward
            [pid_msg.linear.y],     # sideways (unused)
            [pid_msg.linear.z]      # depth
        ])
        pid_vec = (self.motor_matrix @ pid_weights).flatten()
        scaled_pid_vec = np.multiply(self.scale, pid_vec)

        out_vec = (scaled_pid_vec + 1500).clip(1200, 1800)
        
        motor_vals = Motors()
        for i, name in enumerate(self.motor_names):
            setattr(motor_vals, name, int(out_vec[i]))
        self.motor_publisher.publish(motor_vals)

def main(args=None):
    rclpy.init(args=args)

    manager = Thruster_Manager()
    rclpy.spin(manager)

    manager.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
