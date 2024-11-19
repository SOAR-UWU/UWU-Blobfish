"""Motor testing tool."""

import os

import numpy as np
import rclpy
import yaml
from rclpy.node import Node

from blobfish_msgs.msg import Motors

NODE_NAME = "motor_test"
RATE = 30

MOTORS = ["fl", "fr", "ml", "mr", "bl", "br", "bm"]
EXTRA_KEYS = ["enabled", "neutral", "max_rev", "max_fwd", "order"]
MOTOR_MSG_NAMES = [f"motor_{num}" for num in range(1, 8)]

MOTOR_TOPIC = "/blobfish/motor_values"


class MotorTestNode(Node):
    def __init__(self):
        super(MotorTestNode, self).__init__(NODE_NAME)

        self.declare_parameter("config_path", "")
        self.create_timer(1.0 / RATE, self.publish_motor_values)
        self.pub_motors = self.create_publisher(Motors, MOTOR_TOPIC, 0)

        self.enabled = False
        self.neutral = 1500
        self.max_rev = 1100
        self.max_fwd = 1900
        self.order = MOTORS
        self.motor_map = {k: self.neutral for k in MOTORS}

    @property
    def default_config(self):
        return dict(
            enabled=False,
            neutral=1500,
            max_rev=1100,
            max_fwd=1900,
            order=MOTORS,
            **{k: 1500 for k in MOTORS},
        )

    def update_from_config(self):
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
            self.get_logger().warn(f"Config file must be a dict: {cfg_path}")
        except Exception:
            self.get_logger().warn(f"Failed to read config file: {cfg_path}")
        if cfg_dict is None:
            return

        for k, v in cfg_dict.items():
            try:
                if k in MOTORS:
                    self.motor_map[k] = float(v)
                elif k in EXTRA_KEYS:
                    v = type(getattr(self, k))(v)
                    setattr(self, k, v)
                else:
                    self.get_logger().warn(f"Unknown key in config: {k}")
            except Exception:
                self.get_logger().warn(f"Invalid type for key: {k}")

        self.get_logger().info(f"Updated config: {cfg_path}")

    def publish_motor_values(self):
        self.update_from_config()
        if not self.enabled:
            return

        vals = []
        for motor in self.order:
            val = self.motor_map.get(motor, self.neutral)
            vals.append(val)
        vals += [self.neutral] * (len(MOTORS) - len(vals))
        vals = np.clip(vals, self.max_rev, self.max_fwd)

        msg = Motors()
        for name, val in zip(MOTOR_MSG_NAMES, vals):
            setattr(msg, name, int(round(val)))
        self.pub_motors.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = MotorTestNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
