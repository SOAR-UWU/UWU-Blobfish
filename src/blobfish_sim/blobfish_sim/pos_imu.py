"""Simulated version of IMU with built-in position dead reckoning."""

from typing import Optional

import rclpy
from geometry_msgs.msg import TransformStamped, Twist
from scipy.spatial.transform import Rotation
from tf2_msgs.msg import TFMessage

from .base_bridge import create_bridge

GZ_TOPIC = "/gz/blobfish/pose"
ROS_TOPIC = "/blobfish/imu_measurements"

ROBOT_NAME = "blobfish"

# Seems like a happy accident that the IMU rotation frame is the same, or maybe
# Javin actually did configure the VectorNav's frame intentionally.


def map_imu(msg: TFMessage, _) -> Optional[Twist]:
    """Map IMU."""
    pose: TransformStamped = next(
        (p for p in msg.transforms if p.child_frame_id == ROBOT_NAME), None
    )
    if pose is None:
        return

    msg_rot = pose.transform.rotation
    msg_pos = pose.transform.translation

    out = Twist()
    rot = Rotation.from_quat((msg_rot.x, msg_rot.y, msg_rot.z, msg_rot.w))
    rot_x, rot_y, rot_z = rot.as_euler("xyz", degrees=True)
    out.angular.x = rot_x
    out.angular.y = rot_y
    out.angular.z = rot_z
    out.linear.x = msg_pos.x
    out.linear.y = msg_pos.y
    out.linear.z = msg_pos.z
    return out


def main(args=None):
    rclpy.init(args=args)
    node = create_bridge(map_imu, GZ_TOPIC, TFMessage, ROS_TOPIC, Twist, to_profile=0)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
