#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64, Char
from geometry_msgs.msg import Vector3
from rclpy.parameter import Parameter


class Setpoints_Node(Node):
    def __init__(self):
        super().__init__("setpoints_node")
        self.yawpitchroll_pub = self.create_publisher(Vector3, 'blobfish/yawpitchroll_setpoints', 10)
        self.speed_pub = self.create_publisher(Float64, 'blobfish/speed_setpoint', 10)
        self.create_subscription(Char, 'keypress', self.read_keys, 10)
        self.declare_parameter("small_unit", Parameter.Type.DOUBLE)
        self.declare_parameter("big_unit", Parameter.Type.DOUBLE)
        self.small_unit = self.get_parameter("small_unit").value
        self.big_unit = self.get_parameter("big_unit").value
        self.setpoint_control_enabled = False
        self.speed_setpoint = 0.0
        self.yaw_setpoint = 0.0
        self.pitch_setpoint = 0.0
        self.roll_setpoint = 0.0
        
    def read_keys(self, msg):
        keypress = chr(msg.data)

        if self.setpoint_control_enabled:
            if keypress == 'c':
                self.setpoint_control_enabled = False
                self.get_logger().info("Setpoint control disabled")
                return
            
        if not self.setpoint_control_enabled:
            if keypress == 'c':
                self.setpoint_control_enabled = True
                self.get_logger().info("Setpoint control enabled")
            if keypress == 'h':
                self.get_logger().info("Press 'c' to enable manual setpoint control")
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
        elif keypress == 'L':
            self.roll_setpoint -= self.big_unit
        
        if keypress in 'wWsS':
            speed = Float64()
            speed.data = self.speed_setpoint
            self.get_logger().info(f"Speed setpoint: {self.speed_setpoint}")
            self.speed_pub.publish(speed)
        
        elif keypress in 'dDaAiIkKjJlL':
            yawpitchroll = Vector3()
            yawpitchroll.x = self.yaw_setpoint
            yawpitchroll.y = self.pitch_setpoint
            yawpitchroll.z = self.roll_setpoint
            self.get_logger().info(f"Yaw setpoint: {self.yaw_setpoint}")
            self.get_logger().info(f"Pitch setpoint: {self.pitch_setpoint}")
            self.get_logger().info(f"Roll setpoint: {self.roll_setpoint}")
            self.yawpitchroll_pub.publish(yawpitchroll)
        
        # Publish help message
        elif keypress == 'h':
            self.get_logger().info("Press W / S to control speed")
            self.get_logger().info("Press A / D to control yaw")
            self.get_logger().info("Press I / K to control pitch")
            self.get_logger().info("Press J / L to control pitch")
            self.get_logger().info("Press capital letters to change by larger amount, lowercase to change by smaller amount")
            self.get_logger().info("Press c to disable setpoint control")
        
def main(args=None):
    rclpy.init(args=args)

    pid = Setpoints_Node()
    rclpy.spin(pid)

    pid.destroy_node()
    rclpy.shutdown()
    
if __name__ == "__main__":
    main()
