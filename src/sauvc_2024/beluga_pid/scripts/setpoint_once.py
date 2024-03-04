#!/usr/bin/env python3
import rclpy
import numpy as np
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64

class Setpoint_Publisher_Node(Node):
  def __init__(self):
    super().__init__("setpoint_once")
    self.setpoint = Twist()
    self.speed = Float64()
    self.setpoint.linear.x = 0.0
    self.setpoint.linear.y = 0.0
    self.setpoint.linear.z = 0.2
    self.setpoint.angular.x = 0.0
    self.setpoint.angular.y = 0.0
    self.setpoint.angular.z = 0.0
    self.speed.data = 2.0
    self.setpoint_pub = self.create_publisher(Twist, 'beluga/setpoint', 10)
    self.speed_setpoint_pub = self.create_publisher(Float64, 'beluga/speed_setpoint', 10)
    self.publish_setpoint(self.setpoint)

  def publish_setpoint(self, msg):
     self.setpoint_pub.publish(self.setpoint)
     self.speed_setpoint_pub.publish(self.speed)

def main(args=None):
    rclpy.init(args=args)

    setpoint_publisher = Setpoint_Publisher_Node()
    rclpy.spin(setpoint_publisher)

    setpoint_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
