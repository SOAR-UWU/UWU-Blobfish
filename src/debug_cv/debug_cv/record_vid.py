import math
import time
from collections import deque
from datetime import datetime

import cv2
import imutils
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node, SetParametersResult
from rclpy.qos import QoSPresetProfiles
from sensor_msgs.msg import Image
from std_msgs.msg import Char


NODE_NAME = "vid_record"
IMG_TOPIC = "/image_raw"
IMG_TOPIC_NAME = "img_topic"
KEYPRESS_TOPIC = "/keypress"
START_KEY = "g"
STOP_KEY = "G"
SCREENSHOT_KEY = "b"
OUT_FRAMERATE = 60.0
OUT_RESOLUTION = (1280, 720)
DEBUG_RATE = 1.0

QOS_PROFILE = QoSPresetProfiles.SENSOR_DATA.value


class VidRecordNode(Node):
    def __init__(self):
        super(VidRecordNode, self).__init__(NODE_NAME)

        self.declare_parameter(IMG_TOPIC_NAME, IMG_TOPIC)
        self.create_subscription(Char, KEYPRESS_TOPIC, self.keypress_callback, 0)
        self.add_on_set_parameters_callback(self.params_changed)
        self.create_timer(1 / OUT_FRAMERATE, self.write_frame)
        self.create_timer(DEBUG_RATE, self.print_debug)

        self.cv_bridge = CvBridge()
        self.is_recording = False
        self.vid_writer = None
        self.cur_frame = None
        self.cur_sub = None

        # Used for measuring framerate
        self.time_deque = deque([], 10)
        self.last_time = None


    @property
    def img_topic(self):
        return self.get_parameter(IMG_TOPIC_NAME).get_parameter_value().string_value

    def open(self):
        self.is_recording = True

        self.cur_sub = self.create_subscription(
            Image, self.img_topic, self.img_callback, QOS_PROFILE
        )

        filename = f"vid_{self.img_topic.replace('/', '.')}_{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.mp4"
        self._logger.info(f"Opening video file: {filename}")

        # NOTE: Video fps & res is over-specced since detecting the actual fps & res is a hassle
        self.vid_writer = cv2.VideoWriter(
            filename,
            cv2.VideoWriter_fourcc(*"mp4v"),
            OUT_FRAMERATE,
            OUT_RESOLUTION,
        )


    def close(self):
        if not self.is_recording:
            return

        self.vid_writer.release()
        self.destroy_subscription(self.cur_sub)

        self.vid_writer = None
        self.cur_frame = None
        self.cur_sub = None
        self.is_recording = False

        self.time_deque.clear()

    def img_callback(self, msg):
        now = time.time()
        if self.last_time is not None:
            self.time_deque.append(now - self.last_time)
        self.last_time = now

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

    def keypress_callback(self, msg):
        key = chr(msg.data)
        if key == START_KEY:
            self._logger.info("Manual recording triggered!")
            self.close()
            self.open()
        elif key == STOP_KEY:
            self._logger.info("Manual stop triggered!")
            self.close()
        elif key == SCREENSHOT_KEY:
            self._logger.info("Manual screenshot triggered!")
            self.screenshot()

    def screenshot(self):
        sub = None

        def _once(msg):
            nonlocal sub
            self.destroy_subscription(sub)
            img = self.cv_bridge.imgmsg_to_cv2(msg, "bgr8")
            filename = f"img_{self.img_topic.replace('/', '.')}_{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.jpeg"
            cv2.imwrite(filename, img)
            self._logger.info(f"Saved screenshot: {filename}")
        
        sub = self.create_subscription(Image, self.img_topic, _once, QOS_PROFILE)


    def write_frame(self):
        if self.is_recording and self.cur_frame is not None:
            self.vid_writer.write(self.cur_frame)

    def print_debug(self):
        if len(self.time_deque) > 0:
            avg_fps = 1 / (sum(self.time_deque) / len(self.time_deque))
            self._logger.info(f"FPS: {avg_fps:.2f}")
            self.time_deque.popleft()

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
