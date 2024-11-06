"""Replicate `blobfish_sensors/imu_publisher.py`."""

from typing import Optional

import rclpy
from geometry_msgs.msg import Twist
from scipy.spatial.transform import Rotation
from sensor_msgs.msg import Imu

from .base_bridge import create_bridge

GZ_TOPIC = "/gz/blobfish/imu"
ROS_TOPIC = "/blobfish/imu_measurements"

# TODO: IMU_Publisher_Node (kebab-case monstrosity) has a parameter `imu_num_cal_samples`,
# emulate that? There's now a separate list of tasks for the original imu_publisher.py...
# That said, starting with local-frame (rather than global-frame) IMU is basically
# the same thing.


def map_imu(msg: Imu, _) -> Optional[Twist]:
    """Map IMU."""
    out = Twist()
    rot = Rotation.from_quat(
        (msg.orientation.x, msg.orientation.y, msg.orientation.z, msg.orientation.w)
    )
    # xyz is extrinsic, XYZ is intrinsic. Probably is intrinsic?
    rot_x, rot_y, rot_z = rot.as_euler("XYZ", degrees=True)
    out.angular.x = rot_x
    out.angular.y = rot_y
    out.angular.z = rot_z
    out.linear.x = msg.linear_acceleration.x
    out.linear.y = msg.linear_acceleration.y
    out.linear.z = msg.linear_acceleration.z
    # Yes the original node gave up on acceleration values.
    return out


def main(args=None):
    rclpy.init(args=args)
    node = create_bridge(map_imu, GZ_TOPIC, Imu, ROS_TOPIC, Twist, to_profile=0)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
