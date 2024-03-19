from simple_pid import PID
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3
from std_msgs.msg import Char


class PID_Node(Node):
    def __init__(self):
        super().__init__("pid_node")
        self.keypress_sub = self.create_subscription(
            Char, "/keypress", self.proc_keypress, 10)
        self.current_variable = None
        self.current_axis = None
        self.unit = 0.003

        self.declare_parameter("kp_yaw", 0.0)
        self.declare_parameter("ki_yaw", 0.0)
        self.declare_parameter("kd_yaw", 0.0)
        self.declare_parameter("kp_pitch", 0.0)
        self.declare_parameter("ki_pitch", 0.0)
        self.declare_parameter("kd_pitch", 0.0)
        self.declare_parameter("kp_roll", 0.0)
        self.declare_parameter("ki_roll", 0.0)
        self.declare_parameter("kd_roll", 0.0)
        self.declare_parameter("setpoint_yaw", 0.0)
        self.declare_parameter("setpoint_pitch", 0.0)
        self.declare_parameter("setpoint_roll", 0.0)

        kp_yaw = self.get_parameter("kp_yaw").value
        ki_yaw = self.get_parameter("ki_yaw").value
        kd_yaw = self.get_parameter("kd_yaw").value

        kp_pitch = self.get_parameter("kp_pitch").value
        ki_pitch = self.get_parameter("ki_pitch").value
        kd_pitch = self.get_parameter("kd_pitch").value

        kp_roll = self.get_parameter("kp_roll").value
        ki_roll = self.get_parameter("ki_roll").value
        kd_roll = self.get_parameter("kd_roll").value

        self.pid_yaw = PID(kp_yaw, ki_yaw, kd_yaw, output_limits=(-1.0, 1.0), sample_time=0.005, setpoint=0)
        self.pid_pitch = PID(kp_pitch, ki_pitch, kd_pitch, output_limits=(-1.0, 1.0), sample_time=0.005, setpoint=0)
        self.pid_roll = PID(kp_roll, ki_roll, kd_roll, output_limits=(-1.0, 1.0), sample_time=0.005, setpoint=0)
        
        qos_profile = rclpy.qos.qos_profile_sensor_data

        self.yawpitchroll_pid = self.create_publisher(Vector3, 'yawpitchroll_pid', 10)
        self.create_subscription(Vector3, 'imu/corrected_yawpitchroll', self.calculate_pid, qos_profile)
        self.create_subscription(Vector3, 'setpoints/yawpitchroll', self.set_setpoints, 10)

    def calculate_pid(self, msg):
        kp_yaw = self.get_parameter("kp_yaw").value
        ki_yaw = self.get_parameter("ki_yaw").value
        kd_yaw = self.get_parameter("kd_yaw").value

        kp_pitch = self.get_parameter("kp_pitch").value
        ki_pitch = self.get_parameter("ki_pitch").value
        kd_pitch = self.get_parameter("kd_pitch").value

        kp_roll = self.get_parameter("kp_roll").value
        ki_roll = self.get_parameter("ki_roll").value
        kd_roll = self.get_parameter("kd_roll").value
        
        self.pid_yaw.tunings = (kp_yaw, ki_yaw, kd_yaw)
        self.pid_pitch.tunings = (kp_pitch, ki_pitch, kd_pitch)
        self.pid_roll.tunings = (kp_roll, ki_roll, kd_roll)

        current_yaw = msg.x
        current_pitch = msg.y
        current_roll = msg.z

        setpoint_yaw = self.get_parameter("setpoint_yaw").value
        setpoint_pitch = self.get_parameter("setpoint_pitch").value
        setpoint_roll = self.get_parameter("setpoint_roll").value

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
        pid_vals.x = self.pid_yaw(error_yaw)
        pid_vals.y = self.pid_pitch(error_pitch)
        pid_vals.z = self.pid_roll(error_roll)

        self.yawpitchroll_pid.publish(pid_vals)

    def set_setpoints(self, setpoints):
        yaw_setpoint = rclpy.parameter.Parameter(
            "setpoint_yaw",
            rclpy.Parameter.Type.DOUBLE,
            setpoints.x
        )
        pitch_setpoint = rclpy.parameter.Parameter(
            "setpoint_pitch",
            rclpy.Parameter.Type.DOUBLE,
            setpoints.y
        )
        roll_setpoint = rclpy.parameter.Parameter(
            "setpoint_roll",
            rclpy.Parameter.Type.DOUBLE,
            setpoints.z
        )
        
        new_params = [yaw_setpoint, pitch_setpoint, roll_setpoint]
        self.set_paramters(new_params)

    def proc_keypress(self, msg):
        keypress = chr(msg.data)
        if keypress in "pP":
            self.current_variable = "p"
            self.get_logger().info("Tuning P")
        if keypress in "iI":
            self.current_variable = "i"
            self.get_logger().info("Tuning I")
        if keypress in "dD":
            self.current_variable = "d"
            self.get_logger().info("Tuning D")
        if keypress in "rR":
            self.current_axis = "roll"
            self.get_logger().info("Tuning roll")
        if keypress in "tT":
            self.current_axis = "pitch"
            self.get_logger().info("Tuning pitch")
        if keypress in "yY":
            self.current_axis = "yaw"
            self.get_logger().info("Tuning yaw")

        if keypress in "hH":
            self.get_logger().info("Help:")
            self.get_logger().info("P - Tune P")
            self.get_logger().info("I - Tune I")
            self.get_logger().info("D - Tune D")
            self.get_logger().info("R - Tune roll")
            self.get_logger().info("T - Tune pitch")
            self.get_logger().info("Y - Tune yaw")
            self.get_logger().info(", - Decrease")
            self.get_logger().info(". - Increase")
            self.get_logger().info("Current axis: " + str(self.current_axis))
            self.get_logger().info("Current coefficient: " + str(self.current_variable))
        
        if self.current_axis != None and self.current_variable != None:
            if keypress in ",.":
                param_name = f"k{self.current_variable}_{self.current_axis}"
                param_val = self.get_parameter(param_name).value

                if keypress == ",":
                    param_val -= self.unit
                    new_param = rclpy.parameter.Parameter(
                        param_name,
                        rclpy.Parameter.Type.DOUBLE,
                        param_val
                    )
                    self.get_logger().info(f"Decreasing {param_name} to {param_val}")
                if keypress == ".":
                    param_val += self.unit
                    new_param = rclpy.parameter.Parameter(
                        param_name,
                        rclpy.Parameter.Type.DOUBLE,
                        param_val
                    )
                    self.get_logger().info(f"Increasing {param_name} to {param_val}")

                self.set_parameters([new_param])


def main(args=None):
    rclpy.init(args=args)

    pid = PID_Node()
    rclpy.spin(pid)

    pid.destroy_node()
    rclpy.shutdown()
    
if __name__ == "__main__":
    main()
