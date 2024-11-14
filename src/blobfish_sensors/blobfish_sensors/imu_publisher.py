#!/usr/bin/env python3
import rclpy
import math
import numpy as np
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Imu
from sensor_msgs.msg import FluidPressure
from vectornav_msgs.msg import CommonGroup

class IMU_Publisher_Node(Node):
  def __init__(self):
    super().__init__("IMU_publisher")
    self.state = Twist()
    self.state.linear.x = 0.0
    self.state.linear.y = 0.0
    self.state.linear.z = 0.0
    self.state.angular.x = 0.0
    self.state.angular.y = 0.0
    self.state.angular.z = 0.0
    self.state_pub = self.create_publisher(Twist, 'blobfish/imu_measurements', 10)
    self.create_subscription(CommonGroup, 'vectornav/raw/common', self.imu_callback, 10)

    self.count = 0
    self.declare_parameter('imu_num_cal_samples', 100)
    self.imu_num_cal_samples = self.get_parameter('imu_num_cal_samples').value
    self.average_value = 0.0
    self.yaw_calib = 0
    self.pitch_calib = 0
    self.roll_calib = 0

  def imu_callback(self, msg: CommonGroup):
    # quaternion = msg.orientation
    # roll, pitch, yaw = self.euler_from_quaternion(quaternion)
    roll, pitch, yaw = msg.yawpitchroll.z, msg.yawpitchroll.y, msg.yawpitchroll.x
    self.state.angular.x = roll
    self.state.angular.y = pitch
    self.state.angular.z = yaw

    raw_yaw = yaw
    raw_pitch = pitch
    raw_roll = roll
    # raw_accel_x = accel.x
    # raw_accel_y = accel.y   
    # raw_accel_z = accel.z

    if self.count < self.imu_num_cal_samples:
      self.yaw_calib += raw_yaw
      self.pitch_calib += raw_pitch
      self.roll_calib += raw_roll
      # self.acc_x_calib += raw_accel_x
      # self.acc_y_calib += raw_accel_y
      # self.acc_z_calib += raw_accel_z
      self.count+=1
        
    elif self.count == self.imu_num_cal_samples:
      self.average_yaw_value = self.yaw_calib / self.imu_num_cal_samples
      self.average_pitch_value = self.pitch_calib / self.imu_num_cal_samples
      self.average_roll_value = self.roll_calib / self.imu_num_cal_samples
      # average_accel_x_value = self.acc_x_calib / self.imu_num_cal_samples
      # average_accel_y_value = self.acc_y_calib / self.imu_num_cal_samples
      # average_accel_z_value = self.acc_z_calib / self.imu_num_cal_samples
      # self.gravity = math.sqrt(average_accel_x_value**2 + average_accel_y_value**2 + average_accel_z_value**2)
      self.get_logger().info(f"The average calibrated IMU rotational offset value is: {self.average_yaw_value}, {self.average_pitch_value}, {self.average_roll_value}")
      # self.get_logger().info(f"The average calibrated IMU acceleration offset value is: {self.gravity}")
      self.count+=1

    else:
      # quat_msg = msg.orientation
      # Calibrate the IMU data to remove gravity

      # TODO: NOTE: Steal how gravity correction is done here if its correct.
      # quat = [quat_msg.w, quat_msg.x, quat_msg.y, quat_msg.z]
      # raw_accel_vec = [raw_accel_x, raw_accel_y, raw_accel_z]
      # gravity_vec = [0, 0, -self.gravity]
      # gravity_vec = self.quat_rotate(self.quat_inverse(quat), gravity_vec)
      # accel_vec = [raw - grav for raw, grav in zip(raw_accel_vec, gravity_vec)]

      # self.vel_x += accel_vec[0]
      # self.vel_y += accel_vec[1]
      # self.vel_z += accel_vec[2]

      # self.vel_x = 0.0 if abs(self.vel_x) < 0.1 else self.vel_x * 0.99
      # self.vel_y = 0.0 if abs(self.vel_y) < 0.1 else self.vel_y * 0.99
      # self.vel_z = 0.0 if abs(self.vel_z) < 0.1 else self.vel_z * 0.99

      # world_vel = self.quat_rotate(self.quat_inverse(quat), [self.vel_x, self.vel_y, self.vel_z])

      # self.depth += world_vel[2]

      self.state.angular.x = (raw_roll - self.average_roll_value)
      self.state.angular.y = (raw_pitch - self.average_pitch_value)
      self.state.angular.z = (raw_yaw - self.average_yaw_value)
      # self.state.velocity.x = self.vel_x
      # self.state.velocity.y = self.vel_y
      # self.state.velocity.z = self.vel_z
      # self.state.depth = self.depth
      self.state_pub.publish(self.state)

    
  def euler_from_quaternion(self, quaternion):
    
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

    state_publisher = IMU_Publisher_Node()
    rclpy.spin(state_publisher)

    state_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
