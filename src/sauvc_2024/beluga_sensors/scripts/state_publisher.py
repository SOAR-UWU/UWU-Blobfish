#!/usr/bin/env python3
import rclpy
import numpy as np
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Imu
from sensor_msgs.msg import FluidPressure

class State_Publisher_Node(Node):
  def __init__(self):
    super().__init__("state_publisher")
    self.state = Twist()
    self.state.linear.x = 0.0
    self.state.linear.y = 0.0
    self.state.linear.z = 0.0
    self.state.angular.x = 0.0
    self.state.angular.y = 0.0
    self.state.angular.z = 0.0
    self.state_pub = self.create_publisher(Twist, 'beluga/state', 10)
    self.create_subscription(Imu, 'input/imu', self.imu_callback, 10)
    self.create_subscription(FluidPressure, 'input/pressure', self.pressure_callback, 10)

  def imu_callback(self, msg):
    quaternion = [msg.orientation.x, msg.orientation.y, msg.orientation.z, msg.orientation.w]
    roll, pitch, yaw = self.euler_from_quaternion(quaternion)
    self.state.angular.x = roll
    self.state.angular.y = pitch
    self.state.angular.z = yaw
    self.publish_state(self.state)

  def pressure_callback(self, msg):
    pressure = msg.fluid_pressure
    depth = (pressure / 101.1325 - 1) * 10
    self.state.linear.z = depth
    self.publish_state(self.state)
  
  def publish_state(self, msg):
     self.state_pub.publish(self.state)
    
  def euler_from_quaternion(quaternion):
    
    x = quaternion.x
    y = quaternion.y
    z = quaternion.z
    w = quaternion.w

    sinr_cosp = 2 * (w * x + y * z)
    cosr_cosp = 1 - 2 * (x * x + y * y)
    roll = np.arctan2(sinr_cosp, cosr_cosp)

    sinp = 2 * (w * y - z * x)
    pitch = np.arcsin(sinp)

    siny_cosp = 2 * (w * z + x * y)
    cosy_cosp = 1 - 2 * (y * y + z * z)
    yaw = np.arctan2(siny_cosp, cosy_cosp)
    return roll, pitch, yaw

def main(args=None):
    rclpy.init(args=args)

    state_publisher = State_Publisher_Node()
    rclpy.spin(state_publisher)

    state_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
