import math
from datetime import datetime

import cv2
import imutils
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node, SetParametersResult
from rclpy.qos import QoSPresetProfiles
from sensor_msgs.msg import Image

NODE_NAME = "vid_record"
IMG_TOPIC = "/image_raw"
IMG_TOPIC_NAME = "img_topic"
OUT_FRAMERATE = 60.0
OUT_RESOLUTION = (1280, 720)

QOS_PROFILE = QoSPresetProfiles.SENSOR_DATA.value


class VidRecordNode(Node):
    def __init__(self):
        super(VidRecordNode, self).__init__(NODE_NAME)

        self.declare_parameter(IMG_TOPIC_NAME, IMG_TOPIC)

        self.add_on_set_parameters_callback(self.params_changed)
        self.create_timer(1 / OUT_FRAMERATE, self.write_frame)

        self.cv_bridge = CvBridge()
        self.is_recording = False
        self.vid_writer = None
        self.cur_frame = None
        self.cur_sub = None
        self.filename = None

        self.open()

    @property
    def img_topic(self):
        return self.get_parameter(IMG_TOPIC_NAME).get_parameter_value().string_value

    def open(self):
        self.is_recording = True

        self.filename = f"vid_{self.img_topic.replace('/', '.')}_{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.mp4"
        self._logger.info(f"Opening video file: {self.filename}")

        # NOTE: Video fps & res is over-specced since detecting the actual fps & res is a hassle
        self.vid_writer = cv2.VideoWriter(
            self.filename,
            cv2.VideoWriter_fourcc(*"mp4v"),
            OUT_FRAMERATE,
            OUT_RESOLUTION,
        )

        self.cur_sub = self.create_subscription(
            Image, self.img_topic, self.img_callback, QOS_PROFILE
        )

    def close(self):
        if not self.is_recording:
            return

        self.cur_sub.destroy()
        self.vid_writer.release()

        self.vid_writer = None
        self.cur_frame = None
        self.cur_sub = None
        self.filename = None
        self.is_recording = False

    def img_callback(self, msg):
        img = self.cv_bridge.imgmsg_to_cv2(msg, "bgr8")
        tw, th = OUT_RESOLUTION
        h, w, _ = img.shape
        b = h < w
        img = imutils.resize(img, None if b else tw, th if b else None)
        h, w, _ = img.shape
        p = (tw - w if b else th - h) / 2
        img = cv2.copyMakeBorder(
            img,
            0 if b else math.floor(p),
            0 if b else math.ceil(p),
            math.floor(p) if b else 0,
            math.ceil(p) if b else 0,
            cv2.BORDER_CONSTANT,
            value=(0, 0, 0),
        )
        img = imutils.resize(img, tw if b else None, None if b else th)
        self.cur_frame = img[: OUT_RESOLUTION[1], : OUT_RESOLUTION[0], :]

    def write_frame(self):
        if self.is_recording and self.cur_frame is not None:
            self.vid_writer.write(self.cur_frame)

    def params_changed(self, params):
        changed = {p.name for p in params}
        if IMG_TOPIC_NAME in changed:
            self._logger.info(f"New img topic: {self.img_topic}")
            self.close()
            self.open()
        return SetParametersResult(successful=True)


def main():
    rclpy.init()
    node = VidRecordNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.close()
        node.destroy_node()


if __name__ == "__main__":
    main()
