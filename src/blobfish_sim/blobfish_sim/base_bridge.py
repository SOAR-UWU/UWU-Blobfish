"""Minimize code repetitions.

This is intentionally limited in scope to be simpler to understand and prevent me
from attempting to create another ROS2 micro-framework or smth.
"""

from typing import Callable, Optional, TypeVar, Union

from rclpy.node import Node, QoSProfile

__all__ = ["create_bridge_node"]

GZ_MSG_TYPE = TypeVar("GZ_MSG_TYPE")
ROS_MSG_TYPE = TypeVar("ROS_MSG_TYPE")


def create_bridge_node(
    func: Callable[[GZ_MSG_TYPE, Node], Optional[ROS_MSG_TYPE]],
    gz_topic: str,
    gz_type: GZ_MSG_TYPE,
    ros_topic: str,
    ros_type: ROS_MSG_TYPE,
    name: Optional[str] = None,
    qos_profile: Union[QoSProfile, int] = 10,
) -> Node:
    """Creates bridge node to process msg from Gazebo to ROS.

    Note that a separate Gazebo-provided `ros_gz_bridge` package's `parameter_bridge`
    node does the actual msg type mapping. This is to do any post-processing, like
    scaling sensor values, applying transformations or changing the type.
    """
    name = name or f"sim_bridge_{ros_topic.split('/')[-1]}"
    node = Node(name)
    pub = node.create_publisher(ros_type, ros_topic, qos_profile)

    def _callback(msg: GZ_MSG_TYPE):
        val = func(msg, node)
        if val is not None:
            pub.publish(val)

    node.create_subscription(gz_type, gz_topic, _callback, qos_profile)
    return node
