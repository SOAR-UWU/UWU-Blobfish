#!/usr/bin/env python3
from simple_pid import PID
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, Vector3


class PID_Node(Node):
    def __init__(self):
        super().__init__("pid_node")
        # Declare pid coefficients
        self.declare_parameter("kp_r", 0.03)
        self.declare_parameter("ki_r", 0.0)
        self.declare_parameter("kd_r", 0.0)

        self.declare_parameter("kp_p", 0.03)
        self.declare_parameter("ki_p", 0.0)
        self.declare_parameter("kd_p", 0.0)

        self.declare_parameter("kp_h", 0.03)
        self.declare_parameter("ki_h", 0.0)
        self.declare_parameter("kd_h", 0.0)

        self.declare_parameter("kp_x", 0.03)
        self.declare_parameter("ki_x", 0.0)
        self.declare_parameter("kd_x", 0.0)

        self.declare_parameter("kp_y", 0.03)
        self.declare_parameter("ki_y", 0.0)
        self.declare_parameter("kd_y", 0.0)
        
        self.declare_parameter("kp_z", 0.03)
        self.declare_parameter("ki_z", 0.0)
        self.declare_parameter("kd_z", 0.0)
        
        self.declare_parameter("setpoint_r", 0.0)
        self.declare_parameter("setpoint_p", 0.0)
        self.declare_parameter("setpoint_h", 0.0)
        self.declare_parameter("setpoint_x", 0.0)
        self.declare_parameter("setpoint_y", 0.0)
        self.declare_parameter("setpoint_z", 0.0)

        kp_r = self.get_parameter("kp_r").value
        ki_r = self.get_parameter("ki_r").value
        kd_r = self.get_parameter("kd_r").value

        kp_p = self.get_parameter("kp_p").value
        ki_p = self.get_parameter("ki_p").value
        kd_p = self.get_parameter("kd_p").value

        kp_h = self.get_parameter("kp_h").value
        ki_h = self.get_parameter("ki_h").value
        kd_h = self.get_parameter("kd_h").value

        kp_x = self.get_parameter("kp_x").value
        ki_x = self.get_parameter("ki_x").value
        kd_x = self.get_parameter("kd_x").value

        kp_y = self.get_parameter("kp_y").value
        ki_y = self.get_parameter("ki_y").value
        kd_y = self.get_parameter("kd_y").value

        kp_z = self.get_parameter("kp_z").value
        ki_z = self.get_parameter("ki_z").value
        kd_z = self.get_parameter("kd_z").value

        self.pid_r = PID(kp_r, ki_r, kd_r, output_limits=(-1.0, 1.0), sample_time=0.005, setpoint=0)
        self.pid_p = PID(kp_p, ki_p, kd_p, output_limits=(-1.0, 1.0), sample_time=0.005, setpoint=0)
        self.pid_h = PID(kp_h, ki_h, kd_h, output_limits=(-1.0, 1.0), sample_time=0.005, setpoint=0)
        self.pid_x = PID(kp_x, ki_x, kd_x, output_limits=(-1.0, 1.0), sample_time=0.005, setpoint=0)
        self.pid_y = PID(kp_y, ki_y, kd_y, output_limits=(-1.0, 1.0), sample_time=0.005, setpoint=0)
        self.pid_z = PID(kp_z, ki_z, kd_z, output_limits=(-1.0, 1.0), sample_time=0.005, setpoint=0)
        
        qos_profile = rclpy.qos.qos_profile_sensor_data

        self.output_pid = self.create_publisher(Twist, 'beluga/control_effort', 10)
        self.create_subscription(Twist, 'beluga/state', self.calculate_pid, qos_profile)
        self.create_subscription(Vector3, 'beluga/setpoint', self.set_setpoints, 10)
        #get imu data from vectornav/pose topic
        #get x y z from some topic?

    def calculate_pid(self, msg):
        kp_r = self.get_parameter("kp_r").value
        ki_r = self.get_parameter("ki_r").value
        kd_r = self.get_parameter("kd_r").value

        kp_p = self.get_parameter("kp_p").value
        ki_p = self.get_parameter("ki_p").value
        kd_p = self.get_parameter("kd_p").value

        kp_h = self.get_parameter("kp_h").value
        ki_h = self.get_parameter("ki_h").value
        kd_h = self.get_parameter("kd_h").value

        kp_x = self.get_parameter("kp_x").value
        ki_x = self.get_parameter("ki_x").value
        kd_x = self.get_parameter("kd_x").value

        kp_y = self.get_parameter("kp_y").value
        ki_y = self.get_parameter("ki_y").value
        kd_y = self.get_parameter("kd_y").value

        kp_z = self.get_parameter("kp_z").value
        ki_z = self.get_parameter("ki_z").value
        kd_z = self.get_parameter("kd_z").value
        
        self.pid_r.tunings = (kp_r, ki_r, kd_r)
        self.pid_p.tunings = (kp_p, ki_p, kd_p)
        self.pid_h.tunings = (kp_h, ki_h, kd_h)
        self.pid_x.tunings = (kp_x, ki_x, kd_x)
        self.pid_y.tunings = (kp_y, ki_y, kd_y)
        self.pid_z.tunings = (kp_z, ki_z, kd_z)

        current_r = msg.angular.x
        current_p = msg.angular.y
        current_h = msg.angular.z
        #TEMP (A), need to read from actual sensor
        current_x = msg.linear.x
        current_y = msg.linear.y
        current_z = msg.linear.z

        setpoint_r = self.get_parameter("setpoint_r").value
        setpoint_p = self.get_parameter("setpoint_p").value
        setpoint_h = self.get_parameter("setpoint_h").value
        setpoint_x = self.get_parameter("setpoint_x").value
        setpoint_y = self.get_parameter("setpoint_y").value
        setpoint_z = self.get_parameter("setpoint_z").value

        error_r = current_r - setpoint_r
        if error_r < -180:
            error_r += 360
        elif error_r > 180:
            error_r -= 360
        error_p = current_p - setpoint_p
        if error_p < -180:
            error_p += 360
        elif error_p > 180:
            error_p -= 360
        error_h = current_h - setpoint_h
        if error_h < -180:
            error_h += 360
        elif error_h > 180:
            error_h -= 360

        # error_x = current_x - setpoint_x
        # error_y = current_y - setpoint_y
        error_z = current_z - setpoint_z
            
        pid_vals = Twist()
        pid_vals.angular.x = self.pid_r(current_r)
        pid_vals.angular.y = self.pid_p(current_p)
        pid_vals.angular.z = self.pid_h(current_h)
        pid_vals.linear.x = self.pid_x(current_x)
        pid_vals.linear.y = self.pid_y(current_y)
        pid_vals.linear.z = self.pid_z(current_z)

        self.output_pid.publish(pid_vals)

    def set_setpoints(self, setpoints):
        r_setpoint = rclpy.parameter.Parameter(
            "setpoint_r",
            rclpy.Parameter.Type.DOUBLE,
            setpoints.z
        )
        p_setpoint = rclpy.parameter.Parameter(
            "setpoint_p",
            rclpy.Parameter.Type.DOUBLE,
            setpoints.y
        )
        h_setpoint = rclpy.parameter.Parameter(
            "setpoint_h",
            rclpy.Parameter.Type.DOUBLE,
            setpoints.x
        )           
        
        new_params = [h_setpoint, p_setpoint, r_setpoint]
        self.set_paramters(new_params)

def main(args=None):
    rclpy.init(args=args)

    pid = PID_Node()
    rclpy.spin(pid)

    pid.destroy_node()
    rclpy.shutdown()
    
if __name__ == "__main__":
    main()
