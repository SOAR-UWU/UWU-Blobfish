"""ROS specific utilities. Other generic utilities should be in lib.utils."""

from typing import Tuple

from vision_msgs.msg import BoundingBox2D

__all__ = ["cvt_bbox"]


def cvt_bbox(bbox: Tuple[int, int, int, int], vw: int, vh: int):
    """Convert absolute left-top-size to relative center-size bbox."""
    l, t, w, h = bbox
    b = BoundingBox2D()
    b.center.position.x = (l + w / 2) / vw
    b.center.position.y = (t + h / 2) / vh
    b.size_x = w / vw
    b.size_y = h / vh
    return b
