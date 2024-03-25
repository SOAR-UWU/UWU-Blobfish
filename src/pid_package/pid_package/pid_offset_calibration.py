from simple_pid.pid import PID
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from vectornav_msgs.msg import CommonGroup
from rclpy import Parameter
from blobfish_msgs.msg import RotDepthVelocity
import numpy as np
import math

class Offset_Calibration(Node):
    def __init__(self):
        super().__init__("offset_calibrator")

        qos_profile = rclpy.qos.qos_profile_sensor_data
        self.create_subscription(CommonGroup, '/vectornav/raw/common', self.callback, qos_profile)
        
        self.count = 0
        self.declare_parameter('imu_num_cal_samples', 100)
        self.imu_num_cal_samples = self.get_parameter('imu_num_cal_samples').value
        self.average_value = 0.0

        self.imu_offset_publisher = self.create_publisher(RotDepthVelocity, 'imu/corrected_measurements', 10)
        self.get_logger().info("offset calibrator started")

        self.vel_x = 0
        self.vel_y = 0
        self.vel_z = 0
        self.depth = 0
        self.yaw_calib = 0
        self.pitch_calib = 0
        self.roll_calib = 0
        self.acc_x_calib = 0
        self.acc_y_calib = 0
        self.acc_z_calib = 0

    def callback(self, msg):
        yawpitchroll = msg.yawpitchroll
        accel = msg.accel
        raw_yaw = yawpitchroll.x
        raw_pitch = yawpitchroll.y
        raw_roll = yawpitchroll.z
        raw_accel_x = accel.x
        raw_accel_y = accel.y
        raw_accel_z = accel.z

        if self.count < self.imu_num_cal_samples:
            self.yaw_calib += raw_yaw
            self.pitch_calib += raw_pitch
            self.roll_calib += raw_roll
            self.acc_x_calib += raw_accel_x
            self.acc_y_calib += raw_accel_y
            self.acc_z_calib += raw_accel_z
            self.count+=1
            
        elif self.count == self.imu_num_cal_samples:
            self.average_yaw_value = self.yaw_calib / self.imu_num_cal_samples
            self.average_pitch_value = self.pitch_calib / self.imu_num_cal_samples
            self.average_roll_value = self.roll_calib / self.imu_num_cal_samples
            average_accel_x_value = self.acc_x_calib / self.imu_num_cal_samples
            average_accel_y_value = self.acc_y_calib / self.imu_num_cal_samples
            average_accel_z_value = self.acc_z_calib / self.imu_num_cal_samples
            self.gravity = math.sqrt(average_accel_x_value**2 + average_accel_y_value**2 + average_accel_z_value**2)
            self.get_logger().info(f"The average calibrated IMU rotational offset value is: {self.average_yaw_value}, {self.average_pitch_value}, {self.average_roll_value}")
            self.get_logger().info(f"The average calibrated IMU acceleration offset value is: {self.gravity}")
            self.count+=1

        else:
            quat_msg = msg.quaternion
            # Calibrate the IMU data to remove gravity

            quat = [quat_msg.w, quat_msg.x, quat_msg.y, quat_msg.z]
            raw_accel_vec = [raw_accel_x, raw_accel_y, raw_accel_z]
            gravity_vec = [0, 0, -self.gravity]
            gravity_vec = self.quat_rotate(self.quat_inverse(quat), gravity_vec)
            accel_vec = [raw - grav for raw, grav in zip(raw_accel_vec, gravity_vec)]

            self.vel_x += accel_vec[0]
            self.vel_y += accel_vec[1]
            self.vel_z += accel_vec[2]

            self.vel_x = 0.0 if abs(self.vel_x) < 0.1 else self.vel_x * 0.99
            self.vel_y = 0.0 if abs(self.vel_y) < 0.1 else self.vel_y * 0.99
            self.vel_z = 0.0 if abs(self.vel_z) < 0.1 else self.vel_z * 0.99

            world_vel = self.quat_rotate(self.quat_inverse(quat), [self.vel_x, self.vel_y, self.vel_z])

            self.depth += world_vel[2]

            pid_values = RotDepthVelocity()

            pid_values.yawpitchroll.x = raw_yaw - self.average_yaw_value
            pid_values.yawpitchroll.y = raw_pitch - self.average_pitch_value
            pid_values.yawpitchroll.z = raw_roll - self.average_roll_value
            pid_values.velocity.x = self.vel_x
            pid_values.velocity.y = self.vel_y
            pid_values.velocity.z = self.vel_z
            pid_values.depth = self.depth
            self.imu_offset_publisher.publish(pid_values)
        
    def euler_from_quaternion(self, quaternion):
        x = quaternion.x
        y = quaternion.y
        z = quaternion.z
        w = quaternion.w

        sinr = 2 * (w * y - z * x)  
        roll = np.arcsin(sinr)

        sinp_cosr = 2 * (w * x + y * z)
        cosp_cosr = 1 - 2 * (x * x + y * y)
        pitch= np.arctan2(sinp_cosr, cosp_cosr)

        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)
        yaw = np.arctan2(siny_cosp, cosy_cosp)
        return roll, pitch, yaw
    
    @staticmethod
    def quat_inverse(quat):
        """Calculates the inverse of a quaternion.
        Expects a quaternion as a list [w, x, y, z]"""
        return [quat[0], -quat[1], -quat[2], -quat[3]]

    @staticmethod
    def quat_rotate(quat, vec):
        """Applies quaternion rotation on a vector
        Expects a quaternion as a list [w, x, y, z] and a vector as a list [x, y, z]"""
        quat_conj = [quat[0], -quat[1], -quat[2], -quat[3]]
        vec_quat = [0] + vec
        return Offset_Calibration.quat_mul(Offset_Calibration.quat_mul(quat, vec_quat), quat_conj)[1:]

    @staticmethod
    def quat_mul(quat1, quat2):
        """Expects two quaternions as lists [w, x, y, z]"""
        w1, x1, y1, z1 = quat1
        w2, x2, y2, z2 = quat2
        w_out = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
        x_out = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
        y_out = w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2
        z_out = w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2
        return [w_out, x_out, y_out, z_out]


def main():
    rclpy.init()
    node = Offset_Calibration()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

