from simple_pid.pid import PID
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3
from motor_msg.msg import Motors
import numpy as np
from rclpy.parameter import Parameter

class Thruster_Manager(Node):
    def __init__(self):
        super().__init__("thruster_manager")
        
        self.order = ["fl", "fr", "ml", "mr", "bl", "bm", "br"]
        self.param_names = [f"control_{name}" for name in self.order]
        self.motor_names = [f"motor_{name}" for name in self.order]
        self.motor_matrix = np.array([
            # yaw pitch roll
            [-1,   0,    0],    # front left motor
            [1,    0,    0],    # front right motor
            [0,    0,   -1],    # middle left motor
            [0,    0,    1],    # middle right motor
            [1,    0,    0],    # back left motor
            [0,   -1,    0],    # back middle motor
            [-1,   0,    0],    # back right motor
        ], dtype=np.float64)

        self.scale = 300    # how much to scale the pid value
        self.create_subscription(Vector3, '/yawpitchroll_pid', self.calculate_thrusters, 10)
        self.create_subscription(Motors, '/control', self.set_control_thrust, 10)
        self.motor_publisher = self.create_publisher(Motors, '/motor_values', 10)
        self.get_logger().info("Thruster manager started")
        
        for name in self.motor_order:
            self.declare_parameter(name, 0)

    
    def calculate_thrusters(self, pid_msg):
        ctrl_params = self.get_parameters(self.motor_order)
        ctrl_vec = np.array([p.value for p in ctrl_params], dtype=np.float64)
        self.get_logger().info(f"Requested: {ctrl_vec}")

        # [-1, 1]
        pid_weights = np.array([
            [pid_msg.x],
            [pid_msg.y],
            [pid_msg.z]
        ])
        pid_vec = (self.motor_matrix @ pid_weights).flatten()
        pid_vec *= self.scale
        self.get_logger().info(f"PID: {pid_vec}")

        out_vec = (pid_vec + ctrl_vec).clip(1200, 1800)
        self.get_logger().info(f"Final: {out_vec}")
        
        motor_vals = Motors()
        for i, name in enumerate(self.motor_names):
            setattr(motor_vals, name, int(out_vec[i]))
        self.motor_publisher.publish(motor_vals)

    def set_control_thrust(self, extra_thrust):
        params = []
        for motor_name, param_name in zip(self.motor_names, self.param_names):
            param = Parameter(param_name, Parameter.Type.INTEGER, getattr(extra_thrust, motor_name))
            params.append(param)

        self.set_parameters(params)
        self.get_logger().info("Control parameters updated")

def main(args=None):
    rclpy.init(args=args)

    manager = Thruster_Manager()
    rclpy.spin(manager)

    manager.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
