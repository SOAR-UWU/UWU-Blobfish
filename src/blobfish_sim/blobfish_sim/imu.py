"""Replicate `blobfish_sensors/imu_publisher.py`."""

from typing import Optional

import rclpy
from sensor_msgs.msg import Imu

from blobfish_msgs.msg import Kinematics

from .base_bridge import create_bridge

GZ_TOPIC = "/gz/blobfish/imu"
ROS_TOPIC = "/blobfish/imu_measurements"
CORRECT_REAL_IMU_ROTATION = True

# TODO: IMU_Publisher_Node (kebab-case monstrosity) has a parameter `imu_num_cal_samples`,
# emulate that? There's now a separate list of tasks for the original imu_publisher.py...
# That said, starting with local-frame (rather than global-frame) IMU is basically
# the same thing.


def map_imu(msg: Imu, _) -> Optional[Kinematics]:
    """Map IMU."""
    out = Kinematics()
    og_quat = msg.orientation

    # Flip from Gazebo sim to our actual IMU's orientation
    qx = -og_quat.x
    qy = og_quat.y
    qz = -og_quat.z
    qw = og_quat.w

    # Flip from actual IMU orientation to Gazebo sim
    if CORRECT_REAL_IMU_ROTATION:
        qx = -qx
        qz = -qz

    out.p.orientation.x = qx
    out.p.orientation.y = qy
    out.p.orientation.z = qz
    out.p.orientation.w = qw
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
