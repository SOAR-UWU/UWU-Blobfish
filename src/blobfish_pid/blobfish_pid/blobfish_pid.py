import os

import numpy as np
import rclpy
import rclpy.parameter
import yaml
from geometry_msgs.msg import Twist
from rcl_interfaces.msg import Log
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data as QOS
from simple_pid import PID
from std_msgs.msg import Char, Float32, Float64

# TODO: Below code needs to have 2 modes, one where the accumulation is done by
# the node, and the other where it relies on the IMU's dead reckoning.

# NOTE: Below code assumes neutral pitch, and neutral row except when tilt strafing
# for lateral movement.

TILT_ANG = 30

PID_TOPIC = "/blobfish/control_effort"
IMU_TOPIC = "/blobfish/imu_measurements"
STATE_TOPIC = "/blobfish/state_setpoints"
DEPTH_TOPIC = "/blobfish/depth"
KEYPRESS_TOPIC = "/keypress"
KEYPRESS_OUT_TOPIC = "/kpout"


NODE_NAME = "pid_node"


def get_ang_delta(a: float, b: float):
    d = a - b
    if d < -180:
        d += 360
    if d > 180:
        d -= 360
    return d


class PIDNode(Node):
    # fmt: off
    pid_params = [
        "kp_roll", "ki_roll", "kd_roll",
        "kp_pitch", "ki_pitch", "kd_pitch",
        "kp_yaw", "ki_yaw", "kd_yaw",
        "kp_fwd", "ki_fwd", "kd_fwd",
        "kp_lat", "ki_lat", "kd_lat",
        "kp_z", "ki_z", "kd_z",
        "speed_coeff",
    ] # list used instead of set to specify key order when saving to config
    # fmt: on

    def __init__(self):
        super(PIDNode, self).__init__(NODE_NAME)

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

        self.declare_parameter("kp_fwd", 0.03)
        self.declare_parameter("ki_fwd", 0.0)
        self.declare_parameter("kd_fwd", 0.0)

        self.declare_parameter("kp_lat", 0.03)
        self.declare_parameter("ki_lat", 0.0)
        self.declare_parameter("kd_lat", 0.0)

        self.declare_parameter("kp_z", 0.03)
        self.declare_parameter("ki_z", 0.0)
        self.declare_parameter("kd_z", 0.0)

        # Just something to reduce the speed since it's not being put through PID
        self.declare_parameter("speed_coeff", 0.03)

        self.setpoint_roll = 0.0
        self.setpoint_pitch = 0.0
        self.setpoint_yaw = 0.0
        self.setpoint_x = 0.0
        self.setpoint_y = 0.0
        self.setpoint_depth = 0.0

        self.speed = 0.0
        self.speed_coeff = self.get_parameter("speed_coeff").value

        self.pid_r = PID(output_limits=(-1.0, 1.0), sample_time=0.005, setpoint=0)
        self.pid_p = PID(output_limits=(-1.0, 1.0), sample_time=0.005, setpoint=0)
        self.pid_h = PID(output_limits=(-1.0, 1.0), sample_time=0.005, setpoint=0)
        self.pid_f = PID(output_limits=(-1.0, 1.0), sample_time=0.005, setpoint=0)
        self.pid_l = PID(output_limits=(-1.0, 1.0), sample_time=0.005, setpoint=0)
        self.pid_z = PID(output_limits=(-1.0, 1.0), sample_time=0.005, setpoint=0)
        self.update_pid_from_params()

        self.output_pid = self.create_publisher(Twist, PID_TOPIC, 0)
        _kp_log_pub = self.create_publisher(Log, KEYPRESS_OUT_TOPIC, 10)
        self.create_subscription(Twist, IMU_TOPIC, self.calculate_control_effort, QOS)
        self.create_subscription(Twist, STATE_TOPIC, self.set_setpoints, 10)
        self.create_subscription(Char, KEYPRESS_TOPIC, self.proc_keypress, 10)
        self.create_subscription(Float32, DEPTH_TOPIC, self.read_depth, QOS)
        # Deprecated, use set_setpoints instead to move.
        self.create_subscription(Float64, "blobfish/speed_setpoint", self.set_speed, 10)

        # Variable to buffer depth to publish it together with the other values
        self.current_depth = 0.0
        self.current_axis = None
        self.current_variable = None
        self.tuning = False
        self.unit = 0.003
        self.using_depth = True
        self.log_kp = lambda x: _kp_log_pub.publish(Log(name=self.get_name(), msg=x))

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
            try:
                v = type(self.get_parameter(k).value)(v)
            except Exception:
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

        kp_fwd = self.get_parameter("kp_fwd").value
        ki_fwd = self.get_parameter("ki_fwd").value
        kd_fwd = self.get_parameter("kd_fwd").value

        kp_lat = self.get_parameter("kp_lat").value
        ki_lat = self.get_parameter("ki_lat").value
        kd_lat = self.get_parameter("kd_lat").value

        kp_z = self.get_parameter("kp_z").value
        ki_z = self.get_parameter("ki_z").value
        kd_z = self.get_parameter("kd_z").value

        self.pid_r.tunings = (kp_roll, ki_roll, kd_roll)
        self.pid_p.tunings = (kp_pitch, ki_pitch, kd_pitch)
        self.pid_h.tunings = (kp_yaw, ki_yaw, kd_yaw)
        self.pid_f.tunings = (kp_fwd, ki_fwd, kd_fwd)
        self.pid_l.tunings = (kp_lat, ki_lat, kd_lat)
        self.pid_z.tunings = (kp_z, ki_z, kd_z)

    def calculate_control_effort(self, msg: Twist):
        self.update_pid_from_params()
        val = Twist()

        cur_r, cur_p, cur_h = msg.angular.x, msg.angular.y, msg.angular.z
        cur_x, cur_y = msg.linear.x, msg.linear.y
        cur_z = self.current_depth if self.using_depth else msg.linear.z

        # Convert position error to local frame, see proof.webp in this pkg folder
        cos_h, sin_h = np.cos(np.radians(cur_h)), np.sin(np.radians(cur_h))
        rot = np.array([[cos_h, sin_h], [-sin_h, cos_h]])
        err_xy = np.array([cur_x - self.setpoint_x, cur_y - self.setpoint_y])
        err_fwd, err_lat = rot @ err_xy
        err_z = cur_z - self.setpoint_depth

        # local x is forward, local y is lateral
        val.linear.x = self.pid_f(err_fwd)
        val.linear.y = self.pid_l(err_lat)
        val.linear.z = self.pid_z(err_z)

        # Perform tilt strafing for lateral movement
        cur_r -= TILT_ANG * val.linear.y

        # Calculate orientation error
        err_r = get_ang_delta(cur_r, self.setpoint_roll)
        err_p = get_ang_delta(cur_p, self.setpoint_pitch)
        err_h = get_ang_delta(cur_h, self.setpoint_yaw)

        val.angular.x = self.pid_r(err_r)
        val.angular.y = self.pid_p(err_p)
        val.angular.z = self.pid_h(err_h)
        # val.linear.x = self.speed * self.speed_coeff
        # val.linear.y = 0.0   # not correcting for y axis (sideways movement)

        self.output_pid.publish(val)

    def read_depth(self, msg: Float32):
        self.current_depth = msg.data

    def set_setpoints(self, setpoints: Twist):
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
    def proc_keypress(self, msg: Char):
        keypress = chr(msg.data)

        # Disable the use of the depth sensor (current depth always reads 0)
        if keypress == "q":
            self.using_depth = not self.using_depth
            self.log_kp(f"Using depth sensor for control: {self.using_depth}")
            if not self.using_depth:
                self.current_depth = 0

        if not self.tuning:
            if keypress == "h":
                self.log_kp("Press 'c' to tune PID parameters")
                if self.using_depth:
                    self.log_kp("Press 'q' to disable depth reading from sensor")
                else:
                    self.log_kp("Press 'q' to enable depth reading from sensor")
            elif keypress == "c":
                self.log_kp("Tuning PID parameters, press 'c' again to stop")
                self.tuning = True
            return

        if keypress == "c":
            self.log_kp("Tuning for PID parameters stopped, press 'c' again to start")
            self.tuning = False
            return

        if keypress in "pP":
            self.current_variable = "p"
            self.log_kp("Tuning P")
        if keypress in "iI":
            self.current_variable = "i"
            self.log_kp("Tuning I")
        if keypress in "dD":
            self.current_variable = "d"
            self.log_kp("Tuning D")
        if keypress in "rR":
            self.current_axis = "roll"
            self.log_kp("Tuning roll")
        if keypress in "tT":
            self.current_axis = "pitch"
            self.log_kp("Tuning pitch")
        if keypress in "yY":
            self.current_axis = "yaw"
            self.log_kp("Tuning yaw")
        if keypress in "xX":
            self.current_axis = "x"
            self.log_kp("Tuning x")
        if keypress in "uU":
            self.current_axis = "y"
            self.log_kp("Tuning y")
        if keypress in "`":
            self.save_params_to_config()

        if keypress in "hH":
            self.log_kp(
                "Help:\n"
                "` - Save current parameters\n"
                "P - Tune P\n"
                "I - Tune I\n"
                "D - Tune D\n"
                "R - Tune roll\n"
                "T - Tune pitch\n"
                "Y - Tune yaw\n"
                "X - Tune x\n"
                "U - Tune y\n"
                ", - Decrease\n"
                ". - Increase\n"
                f"Current axis: {self.current_axis}\n"
                f"Current coefficient: {self.current_variable}"
            )
            if self.using_depth:
                self.log_kp("Press 'q' to disable depth reading from sensor")
            else:
                self.log_kp("Press 'q' to enable depth reading from sensor")

        if self.current_axis is not None and self.current_variable is not None:
            if keypress in ",.":
                param_name = f"k{self.current_variable}_{self.current_axis}"
                param_val = self.get_parameter(param_name).value

                if keypress == ",":
                    param_val -= self.unit
                    new_param = rclpy.parameter.Parameter(
                        param_name, rclpy.Parameter.Type.DOUBLE, param_val
                    )
                    self.log_kp(f"Decreasing {param_name} to {param_val}")
                if keypress == ".":
                    param_val += self.unit
                    new_param = rclpy.parameter.Parameter(
                        param_name, rclpy.Parameter.Type.DOUBLE, param_val
                    )
                    self.log_kp(f"Increasing {param_name} to {param_val}")

                self.set_parameters([new_param])


def main(args=None):
    rclpy.init(args=args)

    node = PIDNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
