#!/usr/bin/env python3
import rclpy
from rclpy import Node
from std_msgs.msg import Float64
from geometry_msgs.msg import Twist

class SetPoint(Node):
    def __init__(self, node_name: str):
        time = 0
        rate = rclpy.Rate(10)
        self.init_speed = 0.3
        self.init_twist = Twist()

        self.init_twist.angular.x = 0
        self.init_twist.angular.y = 0
        self.init_twist.angular._z = 0

        self.init_twist.linear.x = 0
        self.init_twist.linear.y = 0
        self.init_twist.linear.z = 0

        self.setpoint_publisher_ = self.create_publisher(Twist, 'beluga/setpoint', 10)
        self.speed_publisher_ = self.create_publisher(Float64, 'beluga/speed', 10)
        self.publish()

    def publish(self):
        while rclpy.ok() and self.time < 3:
            self.setpoint_publisher_.publish(self.init_twist)
            self.speed_publisher_.publish(self.init_speed)
            self.rate.sleep()
            self.time+=0.1
    

def main(args=None):
    SetPoint()
    rclpy.spin()

if __name__ == '__main__':
    main()

