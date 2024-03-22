from simple_pid import PID
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3
from uwu_msgs.msg import RotDepthVelocity
from std_msgs.msg import Char


class PID_Node(Node):
    def __init__(self):
        super().__init__("pid_node")
        self.keypress_sub = self.create_subscription(
            Char, "/keypress", self.proc_keypress, 10)
        # self.create_subscription(
        #     RotDepthVelocity, "/pid_setpoints", self.set_setpoints, 10)
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
        self.declare_parameter("kp_x", 0.0)
        self.declare_parameter("ki_x", 0.0)
        self.declare_parameter("kd_x", 0.0)
        self.declare_parameter("kp_y", 0.0)
        self.declare_parameter("ki_y", 0.0)
        self.declare_parameter("kd_y", 0.0)
        self.declare_parameter("kp_depth", 0.0)
        self.declare_parameter("ki_depth", 0.0)
        self.declare_parameter("kd_depth", 0.0)
        self.setpoint_yaw = 0
        self.setpoint_pitch = 0
        self.setpoint_roll = 0
        self.setpoint_vel_x = 0
        self.setpoint_vel_y = 0
        self.setpoint_depth = 0

        kp_yaw = self.get_parameter("kp_yaw").value
        ki_yaw = self.get_parameter("ki_yaw").value
        kd_yaw = self.get_parameter("kd_yaw").value

        kp_pitch = self.get_parameter("kp_pitch").value
        ki_pitch = self.get_parameter("ki_pitch").value
        kd_pitch = self.get_parameter("kd_pitch").value

        kp_roll = self.get_parameter("kp_roll").value
        ki_roll = self.get_parameter("ki_roll").value
        kd_roll = self.get_parameter("kd_roll").value

        kp_x = self.get_parameter("kp_x").value
        ki_x = self.get_parameter("ki_x").value
        kd_x = self.get_parameter("kd_x").value

        kp_y = self.get_parameter("kp_y").value
        ki_y = self.get_parameter("ki_y").value
        kd_y = self.get_parameter("kd_y").value

        kp_depth = self.get_parameter("kp_depth").value
        ki_depth = self.get_parameter("ki_depth").value
        kd_depth = self.get_parameter("kd_depth").value

        self.pid_yaw = PID(kp_yaw, ki_yaw, kd_yaw, output_limits=(-1.0, 1.0), sample_time=0.005, setpoint=0)
        self.pid_pitch = PID(kp_pitch, ki_pitch, kd_pitch, output_limits=(-1.0, 1.0), sample_time=0.005, setpoint=0)
        self.pid_roll = PID(kp_roll, ki_roll, kd_roll, output_limits=(-1.0, 1.0), sample_time=0.005, setpoint=0)
        self.pid_x = PID(kp_x, ki_x, kd_x, output_limits=(-1.0, 1.0), sample_time=0.005, setpoint=0)
        self.pid_y = PID(kp_y, ki_y, kd_y, output_limits=(-1.0, 1.0), sample_time=0.005, setpoint=0)
        self.pid_depth = PID(kp_depth, ki_depth, kd_depth, output_limits=(-1.0, 1.0), sample_time=0.005, setpoint=0)
        
        qos_profile = rclpy.qos.qos_profile_sensor_data

        self.pid_output = self.create_publisher(RotDepthVelocity, 'pid_output', 10)
        self.create_subscription(RotDepthVelocity, 'imu/corrected_yawpitchroll', self.calculate_pid, qos_profile)

    # Unused for now
    def set_setpoints(self, msg):
        self.setpoint_yaw = msg.yawpitchroll.x
        self.setpoint_pitch = msg.yawpitchroll.y
        self.setpoint_roll = msg.yawpitchroll.z
        self.setpoint_vel_x = msg.velocity.x
        self.setpoint_vel_y = msg.velocity.y
        self.setpoint_depth = msg.depth
    
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
        
        kp_x = self.get_parameter("kp_x").value
        ki_x = self.get_parameter("ki_x").value
        kd_x = self.get_parameter("kd_x").value

        kp_y = self.get_parameter("kp_y").value
        ki_y = self.get_parameter("ki_y").value
        kd_y = self.get_parameter("kd_y").value

        kp_depth = self.get_parameter("kp_depth").value
        ki_depth = self.get_parameter("ki_depth").value
        kd_depth = self.get_parameter("kd_depth").value

        self.pid_yaw.tunings = (kp_yaw, ki_yaw, kd_yaw)
        self.pid_pitch.tunings = (kp_pitch, ki_pitch, kd_pitch)
        self.pid_roll.tunings = (kp_roll, ki_roll, kd_roll)
        self.pid_x.tunings = (kp_x, ki_x, kd_x)
        self.pid_y.tunings = (kp_y, ki_y, kd_y)
        self.pid_depth.tunings = (kp_depth, ki_depth, kd_depth)

        current_yaw = msg.yawpitchroll.x
        current_pitch = msg.yawpitchroll.y
        current_roll = msg.yawpitchroll.z
        current_x = msg.velocity.x
        current_y = msg.velocity.y
        current_depth = msg.depth

        error_yaw = current_yaw - self.setpoint_yaw
        if error_yaw < -180:
            error_yaw += 360
        elif error_yaw > 180:
            error_yaw -= 360
        error_pitch = current_pitch - self.setpoint_pitch
        if error_pitch < -180:
            error_pitch += 360
        elif error_pitch > 180:
            error_pitch -= 360
        error_roll = current_roll - self.setpoint_roll
        if error_roll < -180:
            error_roll += 360
        elif error_roll > 180:
            error_roll -= 360

        error_x = current_x - self.setpoint_vel_x
        error_y = current_y - self.setpoint_vel_y
        error_depth = current_depth - self.setpoint_depth

        pid_vals = RotDepthVelocity()
        pid_vals.yawpitchroll.x = self.pid_yaw(error_yaw)
        pid_vals.yawpitchroll.y = self.pid_pitch(error_pitch)
        pid_vals.yawpitchroll.z = self.pid_roll(error_roll)
        pid_vals.velocity.x = self.pid_x(error_x)
        pid_vals.velocity.y = self.pid_pitch(error_y)
        # pid_vals.depth = self.pid_roll(error_depth)

        self.yawpitchroll_pid.publish(pid_vals)

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
        if keypress in "xX":
            self.current_axis = "x"
            self.get_logger().info("Tuning x")
        if keypress in "uU":
            self.current_axis = "y"
            self.get_logger().info("Tuning y")

        if keypress == "c":
            self.setpoint_vel_x += self.unit
            self.get_logger().info(f"New forward setpoint: {self.setpoint_vel_x}")
        if keypress == "C":
            self.setpoint_vel_x -= self.unit
            self.get_logger().info(f"New forward setpoint: {self.setpoint_vel_x}")

        if keypress in "hH":
            self.get_logger().info("Help:")
            self.get_logger().info("P - Tune P")
            self.get_logger().info("I - Tune I")
            self.get_logger().info("D - Tune D")
            self.get_logger().info("R - Tune roll")
            self.get_logger().info("T - Tune pitch")
            self.get_logger().info("Y - Tune yaw")
            self.get_logger().info("X - Tune x")
            self.get_logger().info("U - Tune y")
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
