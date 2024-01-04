from simple_pid.pid import PID
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3
from motor_msg.msg import Motors
import numpy as np

class Thruster_Manager(Node):
    def __init__(self):
        super().__init__("thruster_manager")
        
        self.motor_matrix = np.array([
            # yaw pitch roll
            [1,    0,    0],    # front right motor
            [-1,   0,    0],    # back right motor
            [0,   -1,    0],    # back middle motor
            [1,    0,    0],    # back left motor
            [0,    0,   -1],    # middle left motor
            [0,    0,    1],    # middle right motor
            [-1,   0,    0],    # front left motor
        ])

        self.scale = 300    # how much to scale the pid value
        self.create_subscription(Vector3, '/yawpitchroll_pid', self.calculate_thrusters, 10)
        self.motor_publisher = self.create_publisher(Motors, 'motor_values', 10)
        self.get_logger().info("Thruster manager started")

    
    def calculate_thrusters(self, pid_msg):
        pid_vector = np.array([
            [pid_msg.x],
            [pid_msg.y],
            [pid_msg.z]
        ])
        pid_vector *= self.scale
        outputs = self.motor_matrix @ pid_vector
        outputs += 1500
        motor_vals = Motors()
        motor_vals.motor_fr = int(outputs[0])
        motor_vals.motor_mr = int(outputs[1])
        motor_vals.motor_bm = int(outputs[2])
        motor_vals.motor_bl = int(outputs[3])
        motor_vals.motor_ml = int(outputs[4])
        motor_vals.motor_br = int(outputs[5])
        motor_vals.motor_fl = int(outputs[6])
        self.motor_publisher.publish(motor_vals)

def main(args=None):
    rclpy.init(args=args)

    manager = Thruster_Manager()
    rclpy.spin(manager)

    manager.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
