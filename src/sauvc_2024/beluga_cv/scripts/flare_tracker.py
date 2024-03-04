#!/usr/bin/env python3
import rclpy
import math
import cv2
import numpy as np
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from vision_msgs.msg import BoundingBox2D


class TwoPointLine:
  def __init__(self, cv_line):
    self.x1, self.y1, self.x2, self.y2 = cv_line

  def reverse(self):
    self.x1, self.y1, self.x2, self.y2 = self.x2, self.y2, self.x1, self.y1


class Vector:
  def __init__(self, x, y):
    self.x = x
    self.y = y

  @staticmethod
  def from_line(line):
    return Vector((line.x2 - line.x1), (line.y2 - line.y1))

  def dot(self, other_vec):
    return self.x * other_vec.x + self.y * other_vec.y

  def norm(self):
    return (self.x ** 2 + self.y ** 2) ** 0.5

  def angle(self, other_vec):
    if abs(self.dot(other_vec)/(self.norm()*other_vec.norm())) > 1:
        return 0
    return math.acos(self.dot(other_vec)/(self.norm()*other_vec.norm())) * 180 / math.pi

  def add_vector(self, other_vec):
    return Vector((self.x + other_vec.x), (self.y + other_vec.y))


class FlareTrackerNode(Node):
  def __init__(self):
    self.node_name = 'flare_tracker'
    super().__init__(self.node_name)

    # Create the cv_bridge object
    self.bridge = CvBridge()
    
    self.result_pub = self.create_publisher(BoundingBox2D, 'pos', 10)
    self.debug_pubs = []
    self.image_sub = self.create_subscription(Image, 'image', self.on_new_frame, 10)

  def on_new_frame(self, msg):
    frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
    frame = np.array(frame, dtype=np.uint8)

    result_raw = self.find(frame)

    boundingBox = BoundingBox2D()
    boundingBox.center.x = result_raw[0]
    boundingBox.center.y = result_raw[1]
    boundingBox.size_x = result_raw[2]
    boundingBox.size_y = result_raw[2]

    self.result_pub.publish(boundingBox)

    debug_frames = result_raw[3]
    while len(self.debug_pubs) < len(debug_frames):
      self.debug_pubs.append(self.create_publisher(Image, "debug/channel{}".format(len(self.debug_pubs)), 10))
    for i, frame in enumerate(debug_frames):
      colored = len(frame.shape) == 3
      encoding = 'bgr8' if colored else 'passthrough'
      self.debug_pubs[i].publish(
          self.bridge.cv2_to_imgmsg(frame, encoding))

  def __inital_filter(self, line):
    minimal_dy = 40
    maximal_dx = 20
    if abs(line.x2 - line.x1) < maximal_dx and abs(line.y2 - line.y1) > minimal_dy:
      return True
    return False

  def __parallel_lines(self, lines, line, parallel_lines):
    vect = Vector.from_line(line)
    for i in parallel_lines:
      if (vect.angle(i) - 0) < 5:
          lines.remove(line)
          return None
    parallel_lines.append(vect)
    return None

  def __sub_score_core(self, x):
    return 1/(x**6 + 1)

  def __sub_score(self, value, centre, error_allowed):
    return self.__sub_score_core((value - centre) / error_allowed * 0.5)

  def __secondary_filter(self, line1, line2, h):
    if line1.y2 < line1.y1:
      line1.reverse()
    if line2.y2 < line2.y1:
      line2.reverse()
    vec_L = Vector.from_line(line1)
    vec_R = Vector.from_line(line2)

    # to check the color between the two lines are yellow
    hor = [line1.x1, line1.x2, line2.x1, line2.x2]
    vet = [line1.y1, line1.y2, line2.y1, line2.y2]
    hor.sort()
    vet.sort()
    if hor[1] != hor[2]:
      left, right = hor[1], hor[2]
    else:
      left, right = hor[0], hor[3]

    if vet[1] != vet[2]:
      up, down = vet[1], vet[2]
    else:
      up, down = vet[0], vet[3]

    if not h[left:right, up:down] is None:
      mean = np.mean(h[left:right, up:down])
    else:
      mean = 0

    total_score = 1
    total_score *= self.__sub_score(vec_L.angle(vec_R), 0, 10)
    total_score *= self.__sub_score(vec_L.angle(Vector(1, 0)), 90, 10)
    total_score *= self.__sub_score(abs(line1.x1 - line2.x1), 3, 10)
    total_score *= self.__sub_score(abs(line1.y1 - line2.y1), 3, 10)
    total_score *= self.__sub_score(mean, 60, 15)
    return total_score

  def find(self, frame):
    img = cv2.resize(frame, (640, 360), 0)
    b, _, _ = cv2.split(img)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, _, v = cv2.split(hsv)
    blurred = cv2.GaussianBlur(b, (11, 21), 0)
    edges = cv2.Canny(blurred, 300, 700, apertureSize=5)
    edges = cv2.dilate(edges, np.ones((3, 3), np.uint8))
    minLineLength, maxLineGap = 75, 5
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180,
                            20, None, minLineLength, maxLineGap)
    if lines is not None:
      for l in lines:
          l1 = TwoPointLine(l[0])
          cv2.line(img, (l1.x1, l1.y1), (l1.x2, l1.y2), (0, 255, 0), 1)
      vertical_lines = []
      scores = {}
      for line in lines:
          line1 = TwoPointLine(line[0])
          if self.__inital_filter(line1):
              vertical_lines.append(line1)
      for line1 in vertical_lines:
          for line2 in vertical_lines:
              scores[self.__secondary_filter(
                  line1, line2, h)] = (line1, line2)
      keylist = list(scores.keys())
      if len(keylist) > 0:
          keylist.sort()
          final_line1, final_line2 = scores[keylist[-1]]
          final_line = final_line1

          cv2.line(img, (final_line.x1, final_line.y1),
                    (final_line.x2, final_line.y2), (0, 0, 255), 3)
          return (final_line.x1 + final_line.x2)/2 - 320, 0, abs(final_line.y1-final_line.y2), [b, edges, img]
    return (0, 0, -1, [b, edges, img])

def main(args=None):
   rclpy.init(args=args)
   flare_tracker = FlareTrackerNode()
   rclpy.spin(flare_tracker)
   
if __name__ == "__main__":
  main()