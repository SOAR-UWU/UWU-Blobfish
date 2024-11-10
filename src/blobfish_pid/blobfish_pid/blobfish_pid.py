import os

import rclpy
import rclpy.parameter
import yaml
from geometry_msgs.msg import Twist
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from simple_pid import PID
from std_msgs.msg import Char, Float32, Float64

# TODO:
# PID-ing off acceleration to get it to 0 DOESNT KEEP US ON THE SPOT
# Even water drag can eventually reduce acceleration to 0.
# We have to accumulate acceleration to get drift (in distance/meters) from origin.
# Then PID to move the robot back to origin using the drift as the error.

# TODO: Below code needs to have 2 modes, one where the accumulation is done by
# the node, and the other where it relies on the IMU's dead reckoning.

TILT_ANG = 30


class PID_Node(Node):
    # fmt: off
    pid_params = [
        "kp_roll", "ki_roll", "kd_roll",
        "kp_pitch", "ki_pitch", "kd_pitch",
        "kp_yaw", "ki_yaw", "kd_yaw",
        "kp_x", "ki_x", "kd_x",
        "kp_y", "ki_y", "kd_y",
        "kp_z", "ki_z", "kd_z",
        "speed_coeff",
    ] # list used instead of set to specify key order when saving to config
    # fmt: on

    def __init__(self):
        super().__init__("pid_node")

        self.declare_parameter("config_path", "")

        # Declare pid coefficients
        self.declare_parameter("kp_roll", 0.03)
        self.declare_parameter("ki_roll", 0.0)
        self.declare_parameter("kd_roll", 0.0)

        self.declare_parameter("kp_pitch", 0.03)
        self.declare_parameter("ki_pitch", 0.0)
        self.declare_parameter("kd_pitch", 0.0)

        self.declare_parameter("kp_yaw", 0.03)
        self.declare_parameter("ki_yaw", 0.0)
        self.declare_parameter("kd_yaw", 0.0)

        # Not running PID for X direction (forward/backward)
        self.declare_parameter("kp_x", 0.03)
        self.declare_parameter("ki_x", 0.0)
        self.declare_parameter("kd_x", 0.0)

        # Not running PID for y direction (sideways)
        self.declare_parameter("kp_y", 0.03)
        self.declare_parameter("ki_y", 0.0)
        self.declare_parameter("kd_y", 0.0)

        self.declare_parameter("kp_z", 0.03)
        self.declare_parameter("ki_z", 0.0)
        self.declare_parameter("kd_z", 0.0)

        # Just something to reduce the speed since it's not being put through PID
        self.declare_parameter("speed_coeff", 0.03)

        self.setpoint_roll = 0.0
        self.setpoint_pitch = 0.0
        self.setpoint_yaw = 0.0
        self.setpoint_depth = 0.0
        self.setpoint_x = 0.0
        self.setpoint_y = 0.0
        self.setpoint_z = 0.0

        self.speed = 0.0

        # Variable to buffer depth to publish it together with the other values
        self.current_depth = 0.0

        self.speed_coeff = self.get_parameter("speed_coeff").value

        self.pid_r = PID(output_limits=(-1.0, 1.0), sample_time=0.005, setpoint=0)
        self.pid_p = PID(output_limits=(-1.0, 1.0), sample_time=0.005, setpoint=0)
        self.pid_h = PID(output_limits=(-1.0, 1.0), sample_time=0.005, setpoint=0)
        self.pid_x = PID(output_limits=(-1.0, 1.0), sample_time=0.005, setpoint=0)
        self.pid_y = PID(output_limits=(-1.0, 1.0), sample_time=0.005, setpoint=0)
        self.pid_z = PID(output_limits=(-1.0, 1.0), sample_time=0.005, setpoint=0)
        self.update_pid_from_params()

        self.output_pid = self.create_publisher(
            Twist, "blobfish/control_effort", qos_profile_sensor_data
        )
        self.create_subscription(
            Twist,
            "blobfish/imu_measurements",
            self.calculate_control_effort,
            qos_profile_sensor_data,
        )
        self.create_subscription(
            Twist, "blobfish/state_setpoints", self.set_setpoints, 10
        )
        self.create_subscription(Float64, "blobfish/speed_setpoint", self.set_speed, 10)
        self.create_subscription(Char, "keypress", self.proc_keypress, 10)
        self.create_subscription(
            Float32, "blobfish/depth", self.read_depth, qos_profile_sensor_data
        )

        self.current_depth = 0
        self.current_axis = None
        self.current_variable = None
        self.tuning = False
        self.unit = 0.003
        self.using_depth = True

    # NOTE: Updating params wont update the config file. This is to prevent infinite
    # loops. Changes to params via other means are only temporary until the config
    # file is reloaded.
    def update_params_from_config(self):
        """Update node parameters from config file (specified by parameter) if
        config file has changed."""
        cfg_path = self.get_parameter("config_path").value
        if cfg_path == "":
            self.__last_config_mtime = -1
            return

        try:
            mtime = self.__last_config_mtime
        except AttributeError:
            mtime = -1

        new_mtime = os.path.getmtime(cfg_path)
        if new_mtime == mtime:
            return
        self.__last_config_mtime = new_mtime

        cfg_dict = None
        try:
            with open(cfg_path, "r") as f:
                cfg = yaml.safe_load(f)
                assert isinstance(cfg, dict)
                cfg_dict = cfg
        except AssertionError:
            self.get_logger().warn(f"Config file must be a param map: {cfg_path}")
        except Exception:
            self.get_logger().warn(f"Failed to read config file: {cfg_path}")
        if cfg_dict is None:
            return

        new_params = []
        for k, v in cfg_dict.items():
            if k not in self.pid_params:
                self.get_logger().warn(f"Unknown parameter in config: {k}")
                continue
            val = type(self.get_parameter(k).value)
            if not isinstance(v, val):
                try:
                    v = val(v)
                except ValueError:
                    self.get_logger().warn(f"Invalid type for parameter in config: {k}")
                    continue

            param = rclpy.parameter.Parameter(k, value=v)
            new_params.append(param)

        self.set_parameters(new_params)
        self.get_logger().info(f"Updating parameters from config: {cfg_path}")

    def save_params_to_config(self):
        """Save node parameters to config file (specified by parameter), overwriting
        the file if it exists."""
        cfg_path = self.get_parameter("config_path").value
        if cfg_path == "":
            self.get_logger().warn("No config file specified, can't save")
            return

        new_params = {k: self.get_parameter(k).value for k in self.pid_params}
        with open(cfg_path, "w") as f:
            yaml.safe_dump(new_params, f, sort_keys=False)

        self.get_logger().info(f"Saving parameters to config: {cfg_path}")

    def update_pid_from_params(self):
        """Update PID coefficients from node parameters."""
        self.update_params_from_config()

        kp_roll = self.get_parameter("kp_roll").value
        ki_roll = self.get_parameter("ki_roll").value
        kd_roll = self.get_parameter("kd_roll").value

        kp_pitch = self.get_parameter("kp_pitch").value
        ki_pitch = self.get_parameter("ki_pitch").value
        kd_pitch = self.get_parameter("kd_pitch").value

        kp_yaw = self.get_parameter("kp_yaw").value
        ki_yaw = self.get_parameter("ki_yaw").value
        kd_yaw = self.get_parameter("kd_yaw").value

        kp_x = self.get_parameter("kp_x").value
        ki_x = self.get_parameter("ki_x").value
        kd_x = self.get_parameter("kd_x").value

        kp_y = self.get_parameter("kp_y").value
        ki_y = self.get_parameter("ki_y").value
        kd_y = self.get_parameter("kd_y").value

        kp_z = self.get_parameter("kp_z").value
        ki_z = self.get_parameter("ki_z").value
        kd_z = self.get_parameter("kd_z").value

        self.pid_r.tunings = (kp_roll, ki_roll, kd_roll)
        self.pid_p.tunings = (kp_pitch, ki_pitch, kd_pitch)
        self.pid_h.tunings = (kp_yaw, ki_yaw, kd_yaw)
        self.pid_x.tunings = (kp_x, ki_x, kd_x)
        self.pid_y.tunings = (kp_y, ki_y, kd_y)
        self.pid_z.tunings = (kp_z, ki_z, kd_z)

    def calculate_control_effort(self, msg: Twist):
        self.update_pid_from_params()
        val = Twist()

        current_r = msg.angular.x
        current_p = msg.angular.y
        current_h = msg.angular.z
        current_x = msg.linear.x
        current_y = msg.linear.y
        current_z = self.current_depth

        error_x = current_x - self.setpoint_x
        error_y = current_y - self.setpoint_y
        error_z = current_z - self.setpoint_depth

        val.linear.x = self.pid_x(error_x)
        val.linear.y = self.pid_y(error_y)
        val.linear.z = self.pid_z(error_z)

        # NOTE: The lateral axis changes depending on the yaw angle. The below logic
        # doesn't account for pitch/upside down however. This takes advantage of the
        # coupling between rotation and lateral movement.
        if 45 < abs(current_h) < 135:
            current_r += TILT_ANG * val.linear.x * (1 if current_h >= 0 else -1)
        else:
            current_r += TILT_ANG * val.linear.y * (1 if abs(current_h) > 134 else -1)

        error_r = current_r - self.setpoint_roll
        if error_r < -180:
            error_r += 360
        elif error_r > 180:
            error_r -= 360
        error_p = current_p - self.setpoint_pitch
        if error_p < -180:
            error_p += 360
        elif error_p > 180:
            error_p -= 360
        error_h = current_h - self.setpoint_yaw
        if error_h < -180:
            error_h += 360
        elif error_h > 180:
            error_h -= 360

        val.angular.x = self.pid_r(error_r)
        val.angular.y = self.pid_p(error_p)
        val.angular.z = self.pid_h(error_h)
        # val.linear.x = self.speed * self.speed_coeff
        # val.linear.y = 0.0   # not correcting for y axis (sideways movement)

        self.output_pid.publish(val)

    def read_depth(self, msg):
        if not self.using_depth:
            return
        self.current_depth = msg.data

    def set_setpoints(self, setpoints):
        self.setpoint_roll = setpoints.angular.x
        self.setpoint_pitch = setpoints.angular.y
        self.setpoint_yaw = setpoints.angular.z
        self.setpoint_x = setpoints.linear.x
        self.setpoint_y = setpoints.linear.y
        self.setpoint_depth = setpoints.linear.z
        # self.get_logger().info(
        #     f"Setpoints set: {self.setpoint_depth}, {self.setpoint_roll}, {self.setpoint_pitch}, {self.setpoint_yaw}"
        # )

    def set_speed(self, msg):
        self.speed = msg.data

    # TODO: Remove most tuning keypresses. Tuning from pid.yaml is easier, and this
    # reduces the amount of reserved keypresses.
    def proc_keypress(self, msg):
        keypress = chr(msg.data)

        # Disable the use of the depth sensor (current depth always reads 0)
        if keypress == "q":
            self.using_depth = not self.using_depth
            self.get_logger().info(
                f"Using depth sensor for control: {self.using_depth}"
            )
            if not self.using_depth:
                self.current_depth = 0

        if not self.tuning:
            if keypress == "h":
                self.get_logger().info("Press 'c' to tune PID parameters")
                if self.using_depth:
                    self.get_logger().info(
                        "Press 'q' to disable depth reading from sensor"
                    )
                else:
                    self.get_logger().info(
                        "Press 'q' to enable depth reading from sensor"
                    )
            elif keypress == "c":
                self.get_logger().info("Tuning PID parameters, press 'c' again to stop")
                self.tuning = True
            return

        if keypress == "c":
            self.get_logger().info(
                "Tuning for PID parameters stopped, press 'c' again to start"
            )
            self.tuning = False
            return

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
        if keypress in "`":
            self.save_params_to_config()

        if keypress in "hH":
            self.get_logger().info("Help:")
            self.get_logger().info("` - Save current parameters")
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
            if self.using_depth:
                self.get_logger().info("Press 'q' to disable depth reading from sensor")
            else:
                self.get_logger().info("Press 'q' to enable depth reading from sensor")

        if self.current_axis is not None and self.current_variable is not None:
            if keypress in ",.":
                param_name = f"k{self.current_variable}_{self.current_axis}"
                param_val = self.get_parameter(param_name).value

                if keypress == ",":
                    param_val -= self.unit
                    new_param = rclpy.parameter.Parameter(
                        param_name, rclpy.Parameter.Type.DOUBLE, param_val
                    )
                    self.get_logger().info(f"Decreasing {param_name} to {param_val}")
                if keypress == ".":
                    param_val += self.unit
                    new_param = rclpy.parameter.Parameter(
                        param_name, rclpy.Parameter.Type.DOUBLE, param_val
                    )
                    self.get_logger().info(f"Increasing {param_name} to {param_val}")

                self.set_parameters([new_param])


def main(args=None):
    rclpy.init(args=args)

    pid = PID_Node()
    try:
        rclpy.spin(pid)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
