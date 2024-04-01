from typing import Tuple

import cv2
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node, SetParametersResult
from rclpy.qos import QoSPresetProfiles
from sensor_msgs.msg import Image
from std_msgs.msg import Char
from vision_msgs.msg import BoundingBox2D, BoundingBox2DArray, Point2D

from .lib.describe import describe_opi

NODE_NAME = "detection"

# Subscribers.
IMG_TOPIC = "/image_raw"
KEYPRESS_TOPIC = "/keypress"

# NOTE: Will have to use https://github.com/ros2/message_filters/blob/rolling/src/message_filters/__init__.py.

# Publishers.
BBOX_TOPIC = "~/bbox"
FLARE_BBOX_TOPIC = "~/flare_bbox"
FLARE_CENTER_TOPIC = "~/flare_center"
GATE_BBOX_TOPIC = "~/gate_bbox"
# NOTE: Don't trust gate centroid since part of the gate might be out of frame
# which would distort the centroid towards the wrong direction. Or take advantage
# of that I guess to figure which direction to go.
GATE_CENTER_TOPIC = "~/gate_center"
MASK_TOPIC = "~/mask"
LARGEST_BBOX_TOPIC = "~/largest_bbox"
LARGEST_CENTER_TOPIC = "~/largest_center"
DEBUG_IMG_TOPIC = "~/debug_img"

# Filter out pool that is blue-ish (is this an assumption?)
WATER_LOWER_BOUND = (160, 100, 100)
WATER_UPPER_BOUND = (360, 255, 255)

FLARE_TARGET_HUE = 33
FLARE_HUE_RANGE = 15

GATE_TARGET_SOLIDITY = 0.1
GATE_SOLIDITY_RANGE = 0.05

QOS_PROFILE = QoSPresetProfiles.SENSOR_DATA.value


def _cvt_bbox(bbox: Tuple[int, int, int, int], vw: int, vh: int):
    x, y, w, h = bbox
    b = BoundingBox2D()
    b.center.position.x = (x + w / 2) / vw
    b.center.position.y = (y + h / 2) / vh
    b.size_x = w / vw
    b.size_y = h / vh
    return b


def _get_hue_dist(h1: int, h2: int) -> int:
    return min(abs(h1 - h2), 360 - abs(h1 - h2))


def _int_tuple(t):
    return tuple(map(int, t))


class DetectNode(Node):
    def __init__(self):
        super(DetectNode, self).__init__(NODE_NAME)

        self.cur_sub = self.create_subscription(
            Image, IMG_TOPIC, self.img_callback, QOS_PROFILE
        )

        self.mask_pub = self.create_publisher(Image, MASK_TOPIC, 1)
        self.bbox_pub = self.create_publisher(BoundingBox2DArray, BBOX_TOPIC, 1)
        self.flare_bbox_pub = self.create_publisher(BoundingBox2D, FLARE_BBOX_TOPIC, 1)
        self.flare_center_pub = self.create_publisher(Point2D, FLARE_CENTER_TOPIC, 1)
        self.gate_bbox_pub = self.create_publisher(BoundingBox2D, GATE_BBOX_TOPIC, 1)
        self.gate_center_pub = self.create_publisher(Point2D, GATE_CENTER_TOPIC, 1)
        self.largest_bbox_pub = self.create_publisher(
            BoundingBox2D, LARGEST_BBOX_TOPIC, 1
        )
        self.largest_center_pub = self.create_publisher(
            Point2D, LARGEST_CENTER_TOPIC, 1
        )
        self.debug_img_pub = self.create_publisher(Image, DEBUG_IMG_TOPIC, 1)

        self.cv_bridge = CvBridge()

    def img_callback(self, msg: Image):
        header = msg.header
        im = self.cv_bridge.imgmsg_to_cv2(msg, "bgr8")
        vh, vw, _ = im.shape

        # TODO: parameters to live tune this.
        objs, mask = describe_opi(im, WATER_LOWER_BOUND, WATER_UPPER_BOUND)
        self.mask_pub.publish(self.cv_bridge.cv2_to_imgmsg(mask, "mono8", header))

        bbox_arr = BoundingBox2DArray(header=header)
        bboxes = [_cvt_bbox(o.bbox, vw, vh) for o in objs]
        bbox_arr.boxes = bboxes

        if len(objs) == 0:
            self.bbox_pub.publish(bbox_arr)
            self.debug_img_pub.publish(msg)
            return

        zipped = list(zip(objs, bboxes))

        largest, largest_bbox = max(zipped, key=lambda x: x[0].area)

        # Find the flare. J-H: works now.
        # TODO: Should also take into account the value & saturation.
        colored = [z for z in zipped if z[0].color is not None]
        if len(colored) > 0:
            flare, flare_bbox = min(
                colored,
                key=lambda x: _get_hue_dist(x[0].color[0], FLARE_TARGET_HUE),
            )
            # self._logger.warning(
            #     f"Flare hue: {flare.color[0]}, dist: {_get_hue_dist(flare.color[0], FLARE_TARGET_HUE)}"
            # )

        # Find the gate. J-H: "should work now"
        gate, gate_bbox = min(
            zipped, key=lambda x: abs(x[0].solidity - GATE_TARGET_SOLIDITY)
        )

        if (
            len(colored) > 0
            and _get_hue_dist(flare.color[0], FLARE_TARGET_HUE) < FLARE_HUE_RANGE
        ):
            self.flare_bbox_pub.publish(flare_bbox)
            x, y = flare.center
            self.flare_center_pub.publish(Point2D(x=x / vw, y=y / vh))
        else:
            flare = None

        if abs(gate.solidity - GATE_TARGET_SOLIDITY) < GATE_SOLIDITY_RANGE:
            self.gate_bbox_pub.publish(gate_bbox)
            x, y = gate.center
            self.gate_center_pub.publish(Point2D(x=x / vw, y=y / vh))
        else:
            gate = None

        self.largest_bbox_pub.publish(largest_bbox)
        x, y = largest.center
        self.largest_center_pub.publish(Point2D(x=x / vw, y=y / vh))

        self.bbox_pub.publish(bbox_arr)

        # Visualization (BGR)
        # all the misc stuff detected.
        for o in objs:
            cv2.rectangle(im, o.bbox, (0, 0, 0), 2)
            cv2.circle(im, _int_tuple(o.center), 2, (0, 0, 0), -1)

        # largest object
        cv2.rectangle(im, largest.bbox, (255, 0, 0), 3)
        cv2.circle(im, _int_tuple(largest.center), 3, (255, 0, 0), -1)

        # flare
        if flare is not None:
            cv2.rectangle(im, flare.bbox, (0, 0, 255), 2)
            cv2.circle(im, _int_tuple(flare.center), 2, (255, 0, 255), -1)

        # gate
        if gate is not None:
            cv2.rectangle(im, gate.bbox, (0, 255, 0), 2)
            cv2.circle(im, _int_tuple(gate.center), 2, (0, 255, 0), -1)

        self.debug_img_pub.publish(self.cv_bridge.cv2_to_imgmsg(im, "bgr8", header))


def main():
    rclpy.init()
    node = DetectNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()


if __name__ == "__main__":
    main()
