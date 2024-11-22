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
    quat = msg.orientation
    acc = msg.linear_acceleration

    # Flip from Gazebo sim to our actual IMU's orientation
    qx = -quat.x
    qy = quat.y
    qz = -quat.z
    qw = quat.w
    ax = acc.x
    ay = -acc.y
    az = -acc.z

    # Flip from actual IMU orientation to Gazebo sim
    if CORRECT_REAL_IMU_ROTATION:
        qx, qz = -qx, -qz
        ay, az = -ay, -az

    out.p.orientation.x = qx
    out.p.orientation.y = qy
    out.p.orientation.z = qz
    out.p.orientation.w = qw
    out.a.linear.x = ax
    out.a.linear.y = ay
    out.a.linear.z = az
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
