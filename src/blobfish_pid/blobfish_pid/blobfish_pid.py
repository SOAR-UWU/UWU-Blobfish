#!/usr/bin/env python3
from simple_pid import PID
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
from geometry_msgs.msg import Twist, Vector3


class PID_Node(Node):
    def __init__(self):
        super().__init__("pid_node")
        # Declare pid coefficients
        self.declare_parameter("kp_roll", 0.03)
        self.declare_parameter("ki_roll", 0.0)
        self.declare_parameter("kd_roll", 0.0)

        self.declare_parameter("kp_pitch", 0.03)
        self.declare_parameter("ki_pitch", 0.0)
        self.declare_parameter("kd_pitch", 0.0)

        self.declare_parameter("kp_yaw", 0.03)
        self.declare_parameter("ki_yaw", 0.0)
        self.declare_parameter("kd_yaw", 0.0)

        # Not running PID for X direction (forward/backward)
        # self.declare_parameter("kp_x", 0.03)
        # self.declare_parameter("ki_x", 0.0)
        # self.declare_parameter("kd_x", 0.0)

        # Not running PID for y direction (sideways)
        # self.declare_parameter("kp_y", 0.03)
        # self.declare_parameter("ki_y", 0.0)
        # self.declare_parameter("kd_y", 0.0)
        
        self.declare_parameter("kp_z", 0.03)
        self.declare_parameter("ki_z", 0.0)
        self.declare_parameter("kd_z", 0.0)
        
        self.setpoint_roll = 0.0
        self.setpoint_pitch = 0.0
        self.setpoint_yaw = 0.0
        # self.setpoint_x = 0.0
        # self.setpoint_y = 0.0
        self.setpoint_z = 0.0

        self.speed = 0.0

        kp_roll = self.get_parameter("kp_roll").value
        ki_roll = self.get_parameter("ki_roll").value
        kd_roll = self.get_parameter("kd_roll").value

        kp_pitch = self.get_parameter("kp_pitch").value
        ki_pitch = self.get_parameter("ki_pitch").value
        kd_pitch = self.get_parameter("kd_pitch").value

        kp_yaw = self.get_parameter("kp_yaw").value
        ki_yaw = self.get_parameter("ki_yaw").value
        kd_yaw = self.get_parameter("kd_yaw").value

        # kp_x = self.get_parameter("kp_x").value
        # ki_x = self.get_parameter("ki_x").value
        # kd_x = self.get_parameter("kd_x").value

        # kp_y = self.get_parameter("kp_y").value
        # ki_y = self.get_parameter("ki_y").value
        # kd_y = self.get_parameter("kd_y").value

        kp_z = self.get_parameter("kp_z").value
        ki_z = self.get_parameter("ki_z").value
        kd_z = self.get_parameter("kd_z").value

        self.pid_r = PID(kp_roll, ki_roll, kd_roll, output_limits=(-1.0, 1.0), sample_time=0.005, setpoint=0)
        self.pid_p = PID(kp_pitch, ki_pitch, kd_pitch, output_limits=(-1.0, 1.0), sample_time=0.005, setpoint=0)
        self.pid_h = PID(kp_yaw, ki_yaw, kd_yaw, output_limits=(-1.0, 1.0), sample_time=0.005, setpoint=0)
        # self.pid_x = PID(kp_x, ki_x, kd_x, output_limits=(-1.0, 1.0), sample_time=0.005, setpoint=0)
        # self.pid_y = PID(kp_y, ki_y, kd_y, output_limits=(-1.0, 1.0), sample_time=0.005, setpoint=0)
        self.pid_z = PID(kp_z, ki_z, kd_z, output_limits=(-1.0, 1.0), sample_time=0.005, setpoint=0)
        
        qos_profile = rclpy.qos.qos_profile_sensor_data

        self.output_pid = self.create_publisher(Twist, 'blobfish/control_effort', 10)
        self.create_subscription(Twist, 'blobfish/imu_measurements', self.calculate_control_effort, qos_profile)
        self.create_subscription(Vector3, 'blobfish/yawpitchroll_setpoints', self.set_setpoints, 10)
        self.create_subscription(Float64, 'blobfish/speed_setpoint', self.set_speed, 10)
        #get imu data from vectornav/pose topic
        #get x y z from some topic?

    def calculate_control_effort(self, msg):
        kp_roll = self.get_parameter("kp_roll").value
        ki_roll = self.get_parameter("ki_roll").value
        kd_roll = self.get_parameter("kd_roll").value

        kp_pitch = self.get_parameter("kp_pitch").value
        ki_pitch = self.get_parameter("ki_pitch").value
        kd_pitch = self.get_parameter("kd_pitch").value

        kp_yaw = self.get_parameter("kp_yaw").value
        ki_yaw = self.get_parameter("ki_yaw").value
        kd_yaw = self.get_parameter("kd_yaw").value

        # kp_x = self.get_parameter("kp_x").value
        # ki_x = self.get_parameter("ki_x").value
        # kd_x = self.get_parameter("kd_x").value

        # kp_y = self.get_parameter("kp_y").value
        # ki_y = self.get_parameter("ki_y").value
        # kd_y = self.get_parameter("kd_y").value

        kp_z = self.get_parameter("kp_z").value
        ki_z = self.get_parameter("ki_z").value
        kd_z = self.get_parameter("kd_z").value
        
        self.pid_r.tunings = (kp_roll, ki_roll, kd_roll)
        self.pid_p.tunings = (kp_pitch, ki_pitch, kd_pitch)
        self.pid_h.tunings = (kp_yaw, ki_yaw, kd_yaw)
        # self.pid_x.tunings = (kp_x, ki_x, kd_x)
        # self.pid_y.tunings = (kp_y, ki_y, kd_y)
        self.pid_z.tunings = (kp_z, ki_z, kd_z)

        current_h = msg.angular.x
        current_p = msg.angular.y
        current_r = msg.angular.z
        # current_x = msg.linear.x
        # current_y = msg.linear.y
        current_z = msg.linear.z

        error_r = current_r - self.setpoint_roll
        if error_r < -180:
            error_r += 360
        elif error_r > 180:
            error_r -= 360
        error_p = current_p - self.setpoint_pitch
        if error_p < -180:
            error_p += 360
        elif error_p > 180:
            error_p -= 360
        error_h = current_h - self.setpoint_yaw
        if error_h < -180:
            error_h += 360
        elif error_h > 180:
            error_h -= 360

        # error_x = current_x - setpoint_x
        # error_y = current_y - setpoint_y
        error_z = current_z - self.setpoint_z
            
        pid_vals = Twist()
        pid_vals.angular.x = self.pid_r(error_h)
        pid_vals.angular.y = self.pid_p(error_p)
        pid_vals.angular.z = self.pid_h(error_r)
        pid_vals.linear.x = self.speed
        pid_vals.linear.y = 0.0   # not correcting for y axis (sideways movement)
        pid_vals.linear.z = self.pid_z(error_z)

        self.output_pid.publish(pid_vals)

    def set_setpoints(self, setpoints):
        self.setpoint_roll = setpoints.z
        self.setpoint_pitch = setpoints.y
        self.setpoint_yaw = setpoints.x

    def set_speed(self, msg):
        self.speed = msg.data

def main(args=None):
    rclpy.init(args=args)

    pid = PID_Node()
    rclpy.spin(pid)

    pid.destroy_node()
    rclpy.shutdown()
    
if __name__ == "__main__":
    main()
