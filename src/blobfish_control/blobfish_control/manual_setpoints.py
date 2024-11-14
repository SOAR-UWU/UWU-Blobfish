#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64, Char
from rcl_interfaces.msg import Log
from geometry_msgs.msg import Twist
from rclpy.parameter import Parameter

KEYPRESS_TOPIC = "/keypress"
KEYPRESS_OUT_TOPIC = "/kpout"

class Setpoints_Node(Node):
    def __init__(self):
        super().__init__("setpoints_node")
        self.rph_pub = self.create_publisher(Twist, 'blobfish/state_setpoints', 10)
        self.speed_pub = self.create_publisher(Float64, 'blobfish/speed_setpoint', 10)
        _kp_log_pub = self.create_publisher(Log, KEYPRESS_OUT_TOPIC, 10)
        self.create_subscription(Char, KEYPRESS_TOPIC, self.read_keys, 10)
        self.declare_parameter("small_unit", Parameter.Type.DOUBLE)
        self.declare_parameter("big_unit", Parameter.Type.DOUBLE)
        self.small_unit = self.get_parameter("small_unit").value
        self.big_unit = self.get_parameter("big_unit").value
        self.setpoint_control_enabled = False
        self.speed_setpoint = 0.0
        self.yaw_setpoint = 0.0
        self.pitch_setpoint = 0.0
        self.roll_setpoint = 0.0
        self.depth_setpoint = 0.0
        self.log_kp = lambda x: _kp_log_pub.publish(Log(name=self.get_name(), msg=x))
        
        
    def read_keys(self, msg):
        keypress = chr(msg.data)

        if self.setpoint_control_enabled:
            if keypress == 'z':
                self.setpoint_control_enabled = False
                self.log_kp("Setpoint control disabled")
                return
            
        if not self.setpoint_control_enabled:
            if keypress == 'z':
                self.setpoint_control_enabled = True
                self.log_kp("Setpoint control enabled")
            if keypress == 'h':
                self.log_kp("Press 'z' to enable manual setpoint control")
            return

        if keypress == 'w':
            self.speed_setpoint += self.small_unit
        elif keypress == 'W':
            self.speed_setpoint += self.big_unit
        elif keypress == 's':
            self.speed_setpoint -= self.small_unit
        elif keypress == 'S':
            self.speed_setpoint -= self.big_unit
        elif keypress == 'd':
            self.yaw_setpoint += self.small_unit
        elif keypress == 'D':
            self.yaw_setpoint += self.big_unit
        elif keypress == 'a':
            self.yaw_setpoint -= self.small_unit
        elif keypress == 'A':
            self.yaw_setpoint -= self.big_unit
        elif keypress == 'i':
            self.pitch_setpoint += self.small_unit
        elif keypress == 'I':
            self.pitch_setpoint += self.big_unit
        elif keypress == 'k':
            self.pitch_setpoint -= self.small_unit
        elif keypress == 'K':
            self.pitch_setpoint -= self.big_unit
        elif keypress == 'j':
            self.roll_setpoint += self.small_unit
        elif keypress == 'J':
            self.roll_setpoint += self.big_unit
        elif keypress == 'l':
            self.roll_setpoint -= self.small_unit
        elif keypress == 'T':
            self.depth_setpoint += self.big_unit
        elif keypress == 't':
            self.depth_setpoint += self.small_unit
        elif keypress == 'G':
            self.depth_setpoint -= self.big_unit
        elif keypress == 'g':
            self.depth_setpoint -= self.small_unit
        
        if keypress in 'wWsS':
            speed = Float64()
            speed.data = self.speed_setpoint
            self.log_kp(f"Speed setpoint: {self.speed_setpoint}")
            self.speed_pub.publish(speed)
        
        elif keypress in 'dDaAiIkKjJlLtTgG':
            rphxyz = Twist()
            rphxyz.angular.x = self.roll_setpoint
            rphxyz.angular.y = self.pitch_setpoint
            rphxyz.angular.z = self.yaw_setpoint
            rphxyz.linear.z = self.depth_setpoint
            self.log_kp(
                f"Yaw setpoint: {self.yaw_setpoint}\n"
                f"Pitch setpoint: {self.pitch_setpoint}\n"
                f"Roll setpoint: {self.roll_setpoint}\n"
                f"Depth setpoint: {self.depth_setpoint}"
            )
            self.rph_pub.publish(rphxyz)
        
        # Publish help message
        elif keypress == 'h':
            self.log_kp(
                "Press W / S to control speed\n"
                "Press A / D to control yaw\n"
                "Press I / K to control pitch\n"
                "Press J / L to control pitch\n"
                "Press Y / H to control depth\n"
                "Press capital letters to change by larger amount, lowercase to change by smaller amount\n"
                "Press z to disable setpoint control"
            )
        
def main(args=None):
    rclpy.init(args=args)

    pid = Setpoints_Node()
    rclpy.spin(pid)

    pid.destroy_node()
    rclpy.shutdown()
    
if __name__ == "__main__":
    main()
