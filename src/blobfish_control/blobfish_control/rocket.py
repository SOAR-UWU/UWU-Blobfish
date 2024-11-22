"""

For SAUVC video.

Strategy for sending it forward in a straight line.

"""

#!/usr/bin/env python3
import os
import time

import rclpy
import yaml
from geometry_msgs.msg import Twist, Vector3
from rclpy.node import Node
from std_msgs.msg import Char
from rcl_interfaces.msg import Log

STRAT_STATE_SETPOINTS = "/blobfish/state_setpoints"
STRAT_SPEED_SETPOINTS = "/blobfish/speed_setpoint"
STRAT_IMU = "/blobfish/imu_measurements"
KEYPRESS_TOPIC = "/keypress"
KEYPRESS_OUT_TOPIC = "/kpout"

UPDATE_ROUTINE = 4


class StrategyRocket(Node):
    valid_params = {"speed": [0.0, 0.0, 0.0], "wait": 0}

    def __init__(self):
        super(StrategyRocket, self).__init__("strat_rocket")

        self.create_subscription(Char, KEYPRESS_TOPIC, self.keypress_callback, 0)
        _kp_log_pub = self.create_publisher(Log, KEYPRESS_OUT_TOPIC, 0)
        self.log_kp = lambda x: _kp_log_pub.publish(Log(name=self.get_name(), msg=x))

        self._setpoint_pub = self.create_publisher(Twist, STRAT_STATE_SETPOINTS, 10)
        self._speed_setpoint_pub = self.create_publisher(
            Vector3, STRAT_SPEED_SETPOINTS, 10
        )

        self.declare_parameter("config_path", "")

        self.instruction_set = []

        self.dni = False

        self.create_timer(1 / UPDATE_ROUTINE, self.get_routine)

    def _validate(self, i: dict):
        assert isinstance(i, dict)
        assert len(i.keys()) == 1  # TODO: Make this compatible with multiple keys
        k = list(i.keys())[0]
        assert k in self.valid_params

        if k not in self.valid_params:
            self.get_logger().warn(f"Unknown parameter in config: {k}")

        v = i[k]
        if k == "speed":
            assert len(v) == 3
            for val in range(len(v)):
                v[val] = float(v[val])
        elif k == "wait":
            assert isinstance(v, int)

    def get_routine(self):
        """Updates instruction set to reflect whatever's in the config file"""

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

        cfg_list = None
        self.instruction_set = []
        try:
            with open(cfg_path, "r") as f:
                cfg = yaml.safe_load(f)
                assert isinstance(cfg, list)
                cfg_list = cfg
        except AssertionError:
            self.get_logger().warn(f"Config file must be a param map: {cfg_path}")
        except Exception:
            self.get_logger().warn(f"Failed to read config file: {cfg_path}")
        if cfg_list is None:
            return

        for i in cfg_list:
            try:
                self._validate(i)
                k = list(i.keys())[0]
                v = i[k]
            except Exception:
                self.get_logger().warn(f"Invalid instruction: {i}")
                continue

            self.instruction_set.append([k, v])

        self.get_logger().info(
            "Instruction set updated. Current set:" + str(self.instruction_set)
        )

    def _on_wait(self, t):
        self.get_logger().info(f"waiting for {t}")
        time.sleep(t)

    def _on_update_speed(self, s: list):
        speed = Vector3(x=s[0], y=s[1], z=s[2])
        self._speed_setpoint_pub.publish(speed)
        self.get_logger().info(f"speed set to {s}")

    # Finish routine
    def execute_routine(self):
        self.get_logger().info("Executing routine...")

        self.dni = True
        for i, v in self.instruction_set:
            if i == "speed":
                self._on_update_speed(v)
            elif i == "wait":
                self._on_wait(v)
            else:
                self.get_logger().warn(f"Invalid instruction {i}")

        self.get_logger().info("Current routine complete.")

        self.instruction_set = []
        self.dni = False

    def keypress_callback(self, msg: Char):
        keypress = chr(msg.data)

        if keypress == "h":
            if self.dni:
                self.log_kp("Currently executing...")
            else:
                self.log_kp("Press e to execute current routine.")
                self.log_kp("Press r to refresh current routine.")

        if self.dni:
            pass
        else:
            if keypress == "e":
                self.execute_routine()

            elif keypress == "r":
                self.get_routine()


def main(args=None):
    rclpy.init(args=None)
    strategy = StrategyRocket()
    try:
        rclpy.spin(strategy)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
