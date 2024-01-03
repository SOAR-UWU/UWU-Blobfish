from simple_pid.pid import PID
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3

N_SAMPLES = 1000

class Offset_Calibration(Node):
    def __init__(self):
        super().__init__("offset_calibrator")
        
        self.counter = N_SAMPLES
        self.create_subscription(Vector3, 'imu/yawpitchroll')