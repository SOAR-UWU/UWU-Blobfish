from simple_pid.pid import PID
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3
import time

class Offset_Calibration(Node):
    def __init__(self):
        super().__init__("offset_calibrator")

        self.create_subscription(Vector3, 'imu/yawpitchroll', self.callback)
        
        self.imu_data_list = []

        self.declare_parameter('imu_data_count', 0)
        self.imu_data_count = self.get_parameter('imu_data_count')

        self.declare_parameter('imu_average_value', 0.0)
        self.average_value = self.get_parameter('imu_average_value')


    def callback(self, msg):
        self.imu_data = msg.x
        self.imu_data_list.append(self.imu_data)

 
    def record_imu_data(self):
        total_value_count = 4000

        for count in range(total_value_count):
            rclpy.spin_once(self)
            self.imu_data_count.set_value(count)
            time.sleep(0.01)

        self.average_value.set_value(sum(self.imu_data_list) / total_value_count)
        print(f"The average calibrated IMU offset value is: {self.average_value}")

    
def main():
    rclpy.init()
    node = Offset_Calibration()
    node.record_imu_data()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

