from simple_pid.pid import PID
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3

class Offset_Calibration(Node):
    def __init__(self):
        super().__init__("offset_calibrator")

        self.create_subscription(Vector3, 'imu/yawpitchroll', self.callback)
        self.imu_data_collection = 0
        self.count = 0
        self.declare_parameter('imu_data_count', 4000)
        self.imu_data_count = self.get_parameter('imu_data_count')
        self.declare_parameter('imu_average_value', 0.0)
        self.average_value = self.get_parameter('imu_average_value')

        self.imu_offset_publisher = self.create_publisher(Vector3, 'imu/corrected_yawpitchroll', 10)


    def callback(self, msg):
        if self.count < self.imu_data_count:
            self.imu_data_collection += msg.x
            self.count+=1
            
        elif self.count == self.imu_data_count:
            self.average_value.set_value(self.imu_data_collection / self.imu_data_count)
            self.get_logger().info(f"The average calibrated IMU offset value is: {self.average_value}")
            self.count+=1

        else:
            pid_values = Vector3()

            pid_values.x = msg.x - self.average_value
            pid_values.y = msg.y
            pid_values.z = msg.z
            self.imu_offset_publisher.publish(pid_values)
        

def main():
    rclpy.init()
    node = Offset_Calibration()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

