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
        self.create_subscription(Motors, '/control', self.set_control_thrust, 10)
        self.motor_publisher = self.create_publisher(Motors, '/motor_values', 10)
        self.get_logger().info("Thruster manager started")
        
        self.declare_parameter("control_fr", 0)
        self.declare_parameter("control_mr", 0)
        self.declare_parameter("control_bm", 0)
        self.declare_parameter("control_bl", 0)
        self.declare_parameter("control_ml", 0)
        self.declare_parameter("control_br", 0)
        self.declare_parameter("control_fl", 0)

    
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

        control_vector = self.get_parameters(["control_fr", "control_mr", "control_bm", "control_bl", "control_ml", "control_br", "control_fl"])
        self.get_logger().info(f"{control_vector}")
        control_vector = np.array(control_vector)
        outputs += control_vector.T
        outputs = outputs.clip(1200, 1800)

        motor_vals.motor_fr = int(outputs[0])
        motor_vals.motor_mr = int(outputs[1])
        motor_vals.motor_bm = int(outputs[2])
        motor_vals.motor_bl = int(outputs[3])
        motor_vals.motor_ml = int(outputs[4])
        motor_vals.motor_br = int(outputs[5])
        motor_vals.motor_fl = int(outputs[6])
        self.motor_publisher.publish(motor_vals)

    def set_control_thrust(self, extra_thrust):
        fr = Parameter("control_fr", Parameter.Type.INTEGER, extra_thrust.motor_fr)
        mr = Parameter("control_mr", Parameter.Type.INTEGER, extra_thrust.motor_mr)
        bm = Parameter("control_bm", Parameter.Type.INTEGER, extra_thrust.motor_bm)
        bl = Parameter("control_bl", Parameter.Type.INTEGER, extra_thrust.motor_bl)
        ml = Parameter("control_ml", Parameter.Type.INTEGER, extra_thrust.motor_ml)
        br = Parameter("control_br", Parameter.Type.INTEGER, extra_thrust.motor_br)
        fl = Parameter("control_fl", Parameter.Type.INTEGER, extra_thrust.motor_fl)
        self.set_parameters([fr, mr, bm, bl, ml, br, fl])

        self.get_logger().info("Control parameters updated")

def main(args=None):
    rclpy.init(args=args)

    manager = Thruster_Manager()
    rclpy.spin(manager)

    manager.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
