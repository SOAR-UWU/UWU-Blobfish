import os

import yaml
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import QoSPresetProfiles
from sensor_msgs.msg import Image
from vision_msgs.msg import BoundingBox2D, BoundingBox2DArray

from .lib.detect import detect
from .lib.visualize import visualize
from .ros_utils import cvt_bbox

NODE_NAME = "detection"

# Subscribers.
IMG_TOPIC = "/image_raw"
KEYPRESS_TOPIC = "/keypress"

# NOTE: Will have to use https://github.com/ros2/message_filters/blob/rolling/src/message_filters/__init__.py.

# Publishers.
BBOX_TOPIC = "~/bbox"
FLARE_BBOX_TOPIC = "~/flare_bbox"
GATE_BBOX_TOPIC = "~/gate_bbox"
RED_BBOX_TOPIC = "~/red_bbox"
BLUE_BBOX_TOPIC = "~/blue_bbox"
YELLOW_BBOX_TOPIC = "~/yellow_bbox"
LARGEST_BBOX_TOPIC = "~/largest_bbox"
MASK_TOPIC = "~/mask"
DEBUG_IMG_TOPIC = "~/debug_img"

QOS_PROFILE = QoSPresetProfiles.SENSOR_DATA.value

def get_mtime(path):
    return os.path.getmtime(path)

def load_config(path):
    with open(path, "r") as f:
        return yaml.safe_load(f), get_mtime(path)

class DetectNode(Node):
    def __init__(self):
        super(DetectNode, self).__init__(NODE_NAME)

        self.cur_sub = self.create_subscription(
            Image, IMG_TOPIC, self.img_callback, QOS_PROFILE
        )

        self.bbox_pub = self.create_publisher(BoundingBox2DArray, BBOX_TOPIC, 1)
        self.flare_bbox_pub = self.create_publisher(BoundingBox2D, FLARE_BBOX_TOPIC, 1)
        self.gate_bbox_pub = self.create_publisher(BoundingBox2D, GATE_BBOX_TOPIC, 1)
        self.largest_bbox_pub = self.create_publisher(
            BoundingBox2D, LARGEST_BBOX_TOPIC, 1
        )
        self.red_bbox_pub = self.create_publisher(BoundingBox2D, RED_BBOX_TOPIC, 1)
        self.blue_bbox_pub = self.create_publisher(BoundingBox2D, BLUE_BBOX_TOPIC, 1)
        self.yellow_bbox_pub = self.create_publisher(
            BoundingBox2D, YELLOW_BBOX_TOPIC, 1
        )
        self.mask_pub = self.create_publisher(Image, MASK_TOPIC, 1)
        self.debug_img_pub = self.create_publisher(Image, DEBUG_IMG_TOPIC, 1)

        self.cv_bridge = CvBridge()

        self.declare_parameters(
            namespace="",
            parameters=[
                ("config_path", "/insert/path/here.yaml"),
            ],
        )

        self.cur_cfg = None
        self.cfg_mtime = 0

    @property
    def params(self):
        return {n: p.value for n, p in self._parameters.items()}

    def _update_cfg(self):
        path = self.params["config_path"]
        if self.cur_cfg is None:
            self._logger.info(f"Loading config: {path}")
            self.cur_cfg, self.cfg_mtime = load_config(path)
            return
        if get_mtime(path) > self.cfg_mtime:
            self._logger.info(f"Updating config: {path}")
            self.cur_cfg, self.cfg_mtime = load_config(path)

    def img_callback(self, msg: Image):
        self._update_cfg()
        if not self.cur_cfg:
            self._logger.error(f"Ensure config path is set! Currently: {self.params['config_path']}")
            return

        header = msg.header
        im = self.cv_bridge.imgmsg_to_cv2(msg, "bgr8")
        vh, vw, _ = im.shape

        res = detect(im, **self.cur_cfg)

        if self.mask_pub.get_subscription_count() > 0:
            maskmsg = self.cv_bridge.cv2_to_imgmsg(res["mask"], "mono8", header)
            self.mask_pub.publish(maskmsg)

        if self.debug_img_pub.get_subscription_count() > 0:
            viz = visualize(im, res)
            vizmsg = self.cv_bridge.cv2_to_imgmsg(viz, "bgr8", header)
            self.debug_img_pub.publish(vizmsg)

        bbox_arr = BoundingBox2DArray(header=header)
        bboxes = [cvt_bbox(o.bbox, vw, vh) for o in res["objs"]]
        bbox_arr.boxes = bboxes

        if len(bboxes) == 0:
            self.bbox_pub.publish(bbox_arr)
            return

        if res["flare"] is not None:
            self.flare_bbox_pub.publish(cvt_bbox(res["flare"].bbox, vw, vh))
        else:
            self.flare_bbox_pub.publish(BoundingBox2D())

        if res["gate"] is not None:
            self.gate_bbox_pub.publish(cvt_bbox(res["gate"].bbox, vw, vh))
        else:
            self.gate_bbox_pub.publish(BoundingBox2D())

        if res["largest"] is not None:
            self.largest_bbox_pub.publish(cvt_bbox(res["largest"].bbox, vw, vh))
        else:
            self.largest_bbox_pub.publish(BoundingBox2D())

        if res["red"] is not None:
            self.red_bbox_pub.publish(cvt_bbox(res["red"].bbox, vw, vh))
        else:
            self.red_bbox_pub.publish(BoundingBox2D())

        if res["blue"] is not None:
            self.blue_bbox_pub.publish(cvt_bbox(res["blue"].bbox, vw, vh))
        else:
            self.blue_bbox_pub.publish(BoundingBox2D())

        if res["yellow"] is not None:
            self.yellow_bbox_pub.publish(cvt_bbox(res["yellow"].bbox, vw, vh))
        else:
            self.yellow_bbox_pub.publish(BoundingBox2D())


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
