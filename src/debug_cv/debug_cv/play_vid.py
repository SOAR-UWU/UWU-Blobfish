import cv2
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node, SetParametersResult
from sensor_msgs.msg import Image

NODE_NAME = "vid_play"
IMG_TOPIC = "/image_raw"
IMG_TOPIC_NAME = "img_topic"
KEYPRESS_TOPIC = "/keypress"
START_KEY = "g"
STOP_KEY = "G"
SCREENSHOT_KEY = "b"


class VidRecordNode(Node):
    def __init__(self):
        super(VidRecordNode, self).__init__(NODE_NAME)

        self.declare_parameter(IMG_TOPIC_NAME, IMG_TOPIC)
        self.declare_parameter("video_path", "video.mp4")
        self.img_pub = self.create_publisher(Image, IMG_TOPIC, 1)
        self.add_on_set_parameters_callback(self.params_changed)

        self.cv_bridge = CvBridge()

        self.cur_cap = None
        self.cur_timer = None
        self.open()

    @property
    def img_topic(self):
        return self.get_parameter(IMG_TOPIC_NAME).get_parameter_value().string_value

    @property
    def video_path(self):
        return self.get_parameter("video_path").get_parameter_value().string_value

    def open(self):
        assert self.cur_cap is None, "Video capture already open!"
        self.cur_cap = cv2.VideoCapture(self.video_path)
        if not self.cur_cap.isOpened():
            self._logger.error(
                f"Failed to open {self.video_path}. Waiting for path change..."
            )
            self.close()
            return

        self._logger.info(f"Opened {self.video_path} for playback.")
        fps = int(self.cur_cap.get(cv2.CAP_PROP_FPS))

        self.cur_timer = self.create_timer(1000 / fps, self.play_frame)

    def play_frame(self):
        if self.cur_cap.isOpened():
            _, frame = self.cur_cap.read()
            cur_idx = int(self.cur_cap.get(cv2.CAP_PROP_POS_FRAMES))
            nframes = int(self.cur_cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self._logger.debug(f"FRAME {cur_idx}/{nframes}")
            self.img_pub.publish(self.cv_bridge.cv2_to_imgmsg(frame))
        else:
            self._logger.error("Video capture closed!")
            self.close()

    def close(self):
        if self.cur_cap is not None:
            self.cur_cap.release()
            self.cur_cap = None
        if self.cur_timer is not None:
            self.cur_timer.destroy()
            self.cur_timer = None

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

    def params_changed(self, params):
        changed = {p.name for p in params}
        if IMG_TOPIC_NAME in changed:
            self.img_pub.destroy()
            self.img_pub = self.create_publisher(Image, self.img_topic)
            self._logger.info(f"New img topic: {self.img_topic}")
        if "video_path" in changed:
            self._logger.info(f"New video path: {self.video_path}")
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
