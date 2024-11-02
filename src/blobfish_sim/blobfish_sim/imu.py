"""Replicate `blobfish_sensors/imu_publisher.py`."""

from typing import Optional

import rclpy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Imu

from .base_bridge import create_bridge

GZ_TOPIC = "/gz/blobfish/imu"
ROS_TOPIC = "/blobfish/imu_measurements"

# TODO: IMU_Publisher_Node (kebab-case monstrosity) has a parameter `imu_num_cal_samples`,
# emulate that? There's now a separate list of tasks for the original imu_publisher.py...


def map_imu(msg: Imu, _) -> Optional[Twist]:
    """Map IMU."""
    out = Twist()
    out.angular.x = msg.orientation.x
    out.angular.y = msg.orientation.y
    out.angular.z = msg.orientation.z
    # Yes the original node gave up on acceleration values.
    return out


def main(args=None):
    try:
        rclpy.init(args=args)
        rclpy.spin(create_bridge(map_imu, GZ_TOPIC, Imu, ROS_TOPIC, Twist))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
