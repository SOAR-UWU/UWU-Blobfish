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

STRAT_STATE_SETPOINTS = "/blobfish/state_setpoints"
STRAT_SPEED_SETPOINTS = "/blobfish/speed_setpoint"
STRAT_IMU = "/blobfish/imu_measurements"
STRAT_INIT_DEPTH = Vector3(x=0, y=0, z=0)


class StrategyRocket(Node):
    valid_params = ["speed", "wait"]

    def __init__(self):
        super(StrategyRocket, self).__init__("strat_rocket")

        self._setpoint_pub = self.create_publisher(Twist, STRAT_STATE_SETPOINTS, 10)
        self._speed_setpoint_pub = self.create_publisher(
            Vector3, STRAT_SPEED_SETPOINTS, 10
        )

        self.declare_parameter("config_path", "")

        self.instruction_set = []

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
                assert isinstance(i, dict)
                assert len(i.keys()) == 1 # TODO: Make this compatible with multiple keys
            except Exception:
                self.get_logger().warn(f"Invalid instruction: {i}")
                continue
                
            k = i.keys()[0]
            if k not in self.valid_params:
                self.get_logger().warn(f"Unknown parameter in config: {k}")
                continue
            try:
                v = i[k]
                assert isinstance(v, list)
                assert len(v) == 3
                for val in range(len(v)):
                    v[val] = float(v[val])
            except Exception:
                self.get_logger().warn(f"Invalid type for parameter in config: {k}")
                continue

            self.instruction_set.append([k, v])

        self.get_logger().info(
            "Instruction set updated. Current set:" + str(self.instruction_set)
        )

    def _on_wait(self, t):
        time.sleep(t)

    def _on_update_speed(self, s: list):
        speed = Vector3(x=s[0], y=s[1], z=s[2])
        self._speed_setpoint_pub.publish(speed)

    # Finish routine
    def execute_routine(self):
        for i, v in self.instruction_set:
            if i == "speed":
                self._on_update_speed(v)
            elif i == "wait":
                self._on_wait(v)
            else:
                self.get_logger().warn(f"Invalid instruction {i}")

        self.instruction_set = []


def main(args=None):
    rclpy.init(args=None)
    strategy = StrategyRocket()
    try:
        rclpy.spin(strategy)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
