from simple_pid.pid import PID
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Quaternion, Vector3
from tf_transformations import euler_from_quaternion

class Offset_Calibration(Node):
    def __init__(self):
        super().__init__("offset_calibrator")

        qos_profile = rclpy.qos.qos_profile_sensor_data
        self.create_subscription(Vector3, 'vectornav/pose', self.callback, qos_profile)
        
        self.imu_data_collection = 0
        self.count = 0
        self.declare_parameter('imu_data_count', 4000)
        self.imu_data_count = self.get_parameter('imu_data_count')
        self.declare_parameter('imu_average_value', 0.0)
        self.average_value = self.get_parameter('imu_average_value')

        self.imu_offset_publisher = self.create_publisher(Vector3, 'imu/corrected_yawpitchroll', 10)


    def callback(self, msg):
        euler_angles = euler_from_quaternion([msg.x, msg.y, msg.z, msg.w])

        if self.count < self.imu_data_count:
            self.imu_data_collection += euler_angles[0]
            self.count+=1
            
        elif self.count == self.imu_data_count:
            self.average_value.set_value(self.imu_data_collection / self.imu_data_count)
            self.get_logger().info(f"The average calibrated IMU offset value is: {self.average_value}")
            self.count+=1

        else:
            pid_values = Vector3()

            pid_values.x = euler_angles[0] - self.average_value
            pid_values.y = euler_angles[1]
            pid_values.z = euler_angles[2]
            self.imu_offset_publisher.publish(pid_values)
        

def main():
    rclpy.init()
    node = Offset_Calibration()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

