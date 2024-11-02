"""Replicate the depth sensor part of `arduino_bridge/arduino_listener.py`.

TODO: This never worked in the OG, so I have no idea what the value mapping should be.
"""

from typing import Optional

import rclpy
from ros_gz_interfaces.msg import Altimeter
from std_msgs.msg import Float32

from .base_bridge import create_bridge

GZ_TOPIC = "/gz/blobfish/depth"
ROS_TOPIC = "/blobfish/depth"


def map_depth(msg: Altimeter, _) -> Optional[Float32]:
    """Map depth values."""
    return Float32(data=msg.vertical_position)


def main(args=None):
    rclpy.init(args=args)
    node = create_bridge(
        map_depth, GZ_TOPIC, Altimeter, ROS_TOPIC, Float32, to_profile=0
    )
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
