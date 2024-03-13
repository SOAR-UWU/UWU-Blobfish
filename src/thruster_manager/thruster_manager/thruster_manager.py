from simple_pid.pid import PID
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3
from motor_msg.msg import Motors, MotorOffset
import numpy as np
from rclpy.parameter import Parameter

class Thruster_Manager(Node):
    def __init__(self):
        super().__init__("thruster_manager")
        
        # Control values denotes the extra thrust that is added to the motors
        self.control_values = [f"control_{num}" for num in range(1, 8)]
        self.motor_names = [f"motor_{num}" for num in range(1, 8)]
        self.motors = ["br", "bm", "fl", "fr", "ml", "bl", "mr"]
        
        # The following section reads the motor positions and directions from the
        # parameter server and orders the motors in the correct order in the matrix.
        # The ROS param <motor_name>_order should be a number from 1 to 7, denoting
        # the number of that motor based on the motor_msg.
        motor_vector_collection = {
            "br": [1, 0, 0],
            "bm": [0, 1, 0],
            "fl": [1, 0, 0],
            "fr": [1, 0, 0],
            "ml": [0, 0, 1],
            "bl": [1, 0, 0],
            "mr": [0, 0, 1]
        }
        motor_orders = []
        for i, (motor_name, motor_vector) in enumerate(motor_vector_collection.items()):
            motor_vector = np.array(motor_vector)
            self.declare_parameter(f"{motor_name}_order", i)
            self.declare_parameter(f"{motor_name}_direction", 1)
            motor_pos = self.get_parameter(f"{motor_name}_order")
            motor_dir = self.get_parameter(f"{motor_name}_direction")
            motor_orders.append((motor_pos.value, motor_vector * motor_dir.value))

        motor_orders.sort(key=lambda x: x[0])

        arr = [motor[1] for motor in motor_orders]

        self.motor_matrix = np.array(arr, dtype=np.float64)

        self.scale = 300    # how much to scale the pid value
        self.create_subscription(Vector3, '/yawpitchroll_pid', self.calculate_thrusters, 10)
        self.create_subscription(MotorOffset, '/motor_dir_control', self.set_control_thrust, 10)
        self.motor_publisher = self.create_publisher(Motors, '/motor_values', 10)
        self.get_logger().info("Thruster manager started")
        
        for name in self.control_values:
            self.declare_parameter(name, 0)

    
    def calculate_thrusters(self, pid_msg):
        ctrl_params = self.get_parameters(self.control_values)
        ctrl_direction = self.get_parameters([f"{motor}_direction" for motor in self.motors])
        ctrl_vec = np.array([p.value * d.value for p, d in zip(ctrl_params, ctrl_direction)], dtype=np.float64)
        # self.get_logger().info(f"Requested: {ctrl_vec}")

        # [-1, 1]
        pid_weights = np.array([
            [pid_msg.x],
            [pid_msg.y],
            [pid_msg.z]
        ])
        pid_vec = (self.motor_matrix @ pid_weights).flatten()
        pid_vec *= self.scale
        # self.get_logger().info(f"PID: {pid_vec}")

        out_vec = (pid_vec + ctrl_vec + 1500).clip(1200, 1800)
        
        motor_vals = Motors()
        for i, name in enumerate(self.motor_names):
            setattr(motor_vals, name, int(out_vec[i]))
        self.motor_publisher.publish(motor_vals)

    def set_control_thrust(self, extra_thrust):
        params = []
        for motor_name, param_name in zip(self.motor_names, self.control_values):
            param = Parameter(param_name, Parameter.Type.INTEGER, getattr(extra_thrust, motor_name))
            params.append(param)

        self.set_parameters(params)

def main(args=None):
    rclpy.init(args=args)

    manager = Thruster_Manager()
    rclpy.spin(manager)

    manager.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
