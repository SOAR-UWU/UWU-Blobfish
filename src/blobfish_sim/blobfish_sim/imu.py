"""Replicate `blobfish_sensors/imu_publisher.py`."""

from typing import Optional

import rclpy
from sensor_msgs.msg import Imu

from blobfish_msgs.msg import Kinematics

from .base_bridge import create_bridge

GZ_TOPIC = "/gz/blobfish/imu"
ROS_TOPIC = "/blobfish/imu_measurements"

# TODO: IMU_Publisher_Node (kebab-case monstrosity) has a parameter `imu_num_cal_samples`,
# emulate that? There's now a separate list of tasks for the original imu_publisher.py...
# That said, starting with local-frame (rather than global-frame) IMU is basically
# the same thing.


def map_imu(msg: Imu, _) -> Optional[Kinematics]:
    """Map IMU."""
    out = Kinematics()
    out.p.orientation = msg.orientation
    out.a.linear = msg.linear_acceleration
    return out


def main(args=None):
    rclpy.init(args=args)
    node = create_bridge(map_imu, GZ_TOPIC, Imu, ROS_TOPIC, Kinematics, to_profile=0)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
