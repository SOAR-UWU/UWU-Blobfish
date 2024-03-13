from simple_pid.pid import PID
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseWithCovarianceStamped, Vector3
from rclpy import Parameter
import numpy as np
import math

class Offset_Calibration(Node):
    def __init__(self):
        super().__init__("offset_calibrator")

        qos_profile = rclpy.qos.qos_profile_sensor_data
        self.create_subscription(PoseWithCovarianceStamped, '/vectornav/pose', self.callback, qos_profile)
        
        self.imu_data_collection = 0
        self.count = 0
        self.declare_parameter('imu_num_cal_samples', 100)
        self.imu_num_cal_samples = self.get_parameter('imu_num_cal_samples').value
        self.average_value = 0.0

        self.imu_offset_publisher = self.create_publisher(Vector3, 'imu/corrected_yawpitchroll', 10)
        self.get_logger().info("offset calibrator started")


    def callback(self, msg):
        quat = msg.pose.pose.orientation
        euler_angles = self.euler_from_quaternion(quat)
        euler_angles = list(math.degrees(r) for r in euler_angles)

        if self.count < self.imu_num_cal_samples:
            self.imu_data_collection += euler_angles[0]
            self.count+=1
            
        elif self.count == self.imu_num_cal_samples:
            self.average_value = self.imu_data_collection / self.imu_num_cal_samples
            # ave_val = Parameter("imu_average_value", Parameter.Type.DOUBLE, self.imu_data_collection / self.imu_num_cal_samples)
            # self.set_parameters([ave_val])
            self.get_logger().info(f"The average calibrated IMU offset value is: {self.average_value}")
            self.count+=1

        else:
            pid_values = Vector3()

            pid_values.x = euler_angles[0] - self.average_value
            pid_values.y = euler_angles[1]
            pid_values.z = euler_angles[2]
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


def main():
    rclpy.init()
    node = Offset_Calibration()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

