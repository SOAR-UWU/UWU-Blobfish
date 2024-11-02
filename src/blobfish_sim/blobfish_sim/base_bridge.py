"""Minimize code repetitions.

This is intentionally limited in scope to be simpler to understand and prevent me
from attempting to create another ROS2 micro-framework or smth.
"""

from typing import Callable, Optional, TypeVar, Union

from rclpy.node import Node, QoSProfile
from rclpy.qos import qos_profile_sensor_data

__all__ = ["create_bridge"]

FROM_MSG_TYPE = TypeVar("FROM_MSG_TYPE")
TO_MSG_TYPE = TypeVar("TO_MSG_TYPE")


def create_bridge(
    func: Callable[[FROM_MSG_TYPE, Node], Optional[TO_MSG_TYPE]],
    from_topic: str,
    from_type: FROM_MSG_TYPE,
    to_topic: str,
    to_type: TO_MSG_TYPE,
    name: Optional[str] = None,
    from_profile: Union[QoSProfile, int] = qos_profile_sensor_data,
    to_profile: Union[QoSProfile, int] = 10,
) -> Node:
    """Creates bridge node to process msg from one topic to another, i.e., from
    Gazebo-mapped topic to our used ROS2 topic.

    Note that a separate Gazebo-provided `ros_gz_bridge` package's `parameter_bridge`
    node does the actual msg type mapping. This bridge is to do any post-processing,
    like scaling sensor values, applying transformations or changing the type.
    """
    name = name or f"sim_bridge_{to_topic.split('/')[-1]}"
    node = Node(name)
    pub = node.create_publisher(to_type, to_topic, to_profile)

    def _callback(msg: FROM_MSG_TYPE):
        val = func(msg, node)
        if val is not None:
            pub.publish(val)

    node.create_subscription(from_type, from_topic, _callback, from_profile)
    return node
