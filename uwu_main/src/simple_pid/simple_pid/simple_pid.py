from simple_pid.pid import PID
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3


class PID_Node(Node):
    def __init__(self):
        super().__init__("pid_node")
        self.declare_parameter("kp_yaw", 1)
        self.declare_parameter("ki_yaw", 1)
        self.declare_parameter("kd_yaw", 1)
        self.declare_parameter("kp_pitch", 1)
        self.declare_parameter("ki_pitch", 1)
        self.declare_parameter("kd_pitch", 1)
        self.declare_parameter("kp_roll", 1)
        self.declare_parameter("ki_roll", 1)
        self.declare_parameter("kd_roll", 1)

        kp_yaw = self.get_parameter("kp_yaw")
        ki_yaw = self.get_parameter("ki_yaw")
        kd_yaw = self.get_parameter("kd_yaw")

        kp_pitch = self.get_parameter("kp_pitch")
        ki_pitch = self.get_parameter("ki_pitch")
        kd_pitch = self.get_parameter("kd_pitch")

        kp_roll = self.get_parameter("kp_roll")
        ki_roll = self.get_parameter("ki_roll")
        kd_roll = self.get_parameter("kd_roll")

        self.pid_yaw = PID(kp_yaw, ki_yaw, kd_yaw, output_limits=(-1, 1), sample_time=0.005, setpoint=0)
        self.pid_pitch = PID(kp_pitch, ki_pitch, kd_pitch, output_limits=(-1, 1), sample_time=0.005, setpoint=0)
        self.pid_roll = PID(kp_roll, ki_roll, kd_roll, output_limits=(-1, 1), sample_time=0.005, setpoint=0)
        
        qos_profile = rclpy.qos.qos_profile_sensor_data

        self.yawpitchroll_pid = self.create_publisher(Vector3, 'yawpitchroll_pid', 10)
        self.create_subscription(Vector3, 'imu/yawpitchroll', self.calculate_pid, qos_profile)
        self.create_subscription(Vector3, 'setpoints/yawpitchroll', self.set_setpoints, 10)

    def calculate_pid(self, msg):
        kp_yaw = self.get_parameter("kp_yaw")
        ki_yaw = self.get_parameter("ki_yaw")
        kd_yaw = self.get_parameter("kd_yaw")

        kp_pitch = self.get_parameter("kp_pitch")
        ki_pitch = self.get_parameter("ki_pitch")
        kd_pitch = self.get_parameter("kd_pitch")

        kp_roll = self.get_parameter("kp_roll")
        ki_roll = self.get_parameter("ki_roll")
        kd_roll = self.get_parameter("kd_roll")
        
        self.pid_yaw.tunings = (kp_yaw, ki_yaw, kd_yaw)
        self.pid_pitch.tunings = (kp_pitch, ki_pitch, kd_pitch)
        self.pid_roll.tunings = (kp_roll, ki_roll, kd_roll)

        current_yaw = msg.x
        current_pitch = msg.y
        current_roll = msg.z

        setpoint_yaw = self.get_parameter("setpoint_yaw")
        setpoint_pitch = self.get_parameter("setpoint_pitch")
        setpoint_roll = self.get_parameter("setpoint_roll")

        error_yaw = current_yaw - setpoint_yaw
        if error_yaw < -180:
            error_yaw += 360
        elif error_yaw > 180:
            error_yaw -= 360
        error_pitch = current_pitch - setpoint_pitch
        if error_pitch < -180:
            error_pitch += 360
        elif error_pitch > 180:
            error_pitch -= 360
        error_roll = current_roll - setpoint_roll
        if error_roll < -180:
            error_roll += 360
        elif error_roll > 180:
            error_roll -= 360

        pid_vals = Vector3()
        pid_vals.x = self.pid_yaw(current_yaw)
        pid_vals.y = self.pid_pitch(current_pitch)
        pid_vals.z = self.pid_roll(current_roll)

        self.yawpitchroll_pid.publish(pid_vals)

    def set_setpoints(self, setpoints):
        yaw_setpoint = rclpy.parameter.Parameter(
            "setpoint_yaw",
            rclpy.Parameter.Type.DOUBLE,
            setpoints.x
        )
        pitch_setpoint = rclpy.parameter.Parameter(
            "setpoint_yaw",
            rclpy.Parameter.Type.DOUBLE,
            setpoints.y
        )
        roll_setpoint = rclpy.parameter.Parameter(
            "setpoint_yaw",
            rclpy.Parameter.Type.DOUBLE,
            setpoints.z
        )
        
        new_params = [yaw_setpoint, pitch_setpoint, roll_setpoint]
        self.set_paramters(new_params)
