"""Simulated version of IMU with built-in position dead reckoning."""

from typing import Optional

import rclpy
from geometry_msgs.msg import TransformStamped
from tf2_msgs.msg import TFMessage

from blobfish_msgs.msg import Kinematics

from .base_bridge import create_bridge

GZ_TOPIC = "/gz/blobfish/pose"
ROS_TOPIC = "/blobfish/imu_measurements"

ROBOT_NAME = "blobfish"

# Seems like a happy accident that the IMU rotation frame is the same, or maybe
# Javin actually did configure the VectorNav's frame intentionally.


def map_imu(msg: TFMessage, _) -> Optional[Kinematics]:
    """Map IMU."""
    pose: TransformStamped = next(
        (p for p in msg.transforms if p.child_frame_id == ROBOT_NAME), None
    )
    if pose is None:
        return

    msg_rot = pose.transform.rotation
    msg_pos = pose.transform.translation

    out = Kinematics()
    out.p.orientation = msg_rot
    out.p.position.x = msg_pos.x
    out.p.position.y = msg_pos.y
    out.p.position.z = msg_pos.z
    return out


def main(args=None):
    rclpy.init(args=args)
    node = create_bridge(
        map_imu, GZ_TOPIC, TFMessage, ROS_TOPIC, Kinematics, to_profile=0
    )
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
