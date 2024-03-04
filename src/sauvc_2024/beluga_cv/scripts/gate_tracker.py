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


class GateTrackerNode(Node):
	def __init__(self):
		self.node_name = 'gate_tracker'
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
			self.debug_pubs[i].publish(self.bridge.cv2_to_imgmsg(frame, encoding))  

	def __possible_line(self, line):
		minimal_dy = 70
		maximal_dx = 40
		if abs(line.x2 - line.x1) < maximal_dx and abs(line.y2 - line.y1) > minimal_dy:
				return True
		return False

	def __sub_score_core(self, x):
		return 1/(x**6 + 1)

	def __sub_score(self, value, centre, error_allowed):
		return self.__sub_score_core((value - centre) / error_allowed * 0.5)

	def __possible_gate(self, gate):
		line1, line2 = gate
		# make sure two lines are from button(1) to top(2)
		if line1.y2 < line1.y1:
			line1.reverse()
		if line2.y2 < line2.y1:
			line2.reverse()
		# if two lines cross, can not be gate
		if (line1.x1 - line2.x1) * (line1.x2 - line2.x2) < 0:
			return False
		# find the left one and the right one
		line_L, line_R = (
			line1, line2) if line1.x1 < line2.x1 else (line2, line1)
		# find the top and button one, from left(1) to right(2)
		line_U = TwoPointLine(
			(line_L.x2, line_L.y2, line_R.x2, line_R.y2))
		line_D = TwoPointLine(
			(line_L.x1, line_L.y1, line_R.x1, line_R.y1))

			# convert to vector
		vec_L = Vector.from_line(line_L)
		vec_R = Vector.from_line(line_R)
		vec_U = Vector.from_line(line_U)
		vec_D = Vector.from_line(line_D)
		if vec_U.norm() == 0 or vec_D.norm() == 0:
			return 0

		total_score = 1

			# check parallel
		total_score *= self.__sub_score(vec_L.angle(vec_R), 0, 10)
		# check perpendicular
		total_score *= self.__sub_score(vec_L.angle(vec_U), 90, 20)
		total_score *= self.__sub_score(vec_R.angle(vec_U), 90, 20)
		total_score *= self.__sub_score(vec_L.angle(vec_D), 90, 20)
		total_score *= self.__sub_score(vec_R.angle(vec_D), 90, 20)
		# check ratio
		total_score *= self.__sub_score(
			(vec_L.add_vector(vec_R).norm() / vec_D.add_vector(vec_U).norm()), 1, 0.5)
		# check vertical
		x_vec = Vector(1, 0)
		total_score *= self.__sub_score(x_vec.angle(vec_L), 90, 30)
		total_score *= self.__sub_score(x_vec.angle(vec_R), 90, 30)

		return total_score

	def find(self, frame):
		# Splite channelsec
		b, g, r = cv2.split(frame)

		# Find edges
		blurred = cv2.GaussianBlur(b, (11, 31), 0)
		edges = cv2.Canny(blurred, 300, 700, apertureSize=5)
		edges = cv2.dilate(edges, np.ones((3, 3), np.uint8))

		# find lines
		lines_frame = frame.copy()
		results_frame = frame.copy()  # np.zeros(b.shape, np.uint8)
		minLineLength = 50
		maxLineGap = 15
		lines = cv2.HoughLinesP(edges, 1, np.pi/360, 20, None,
			minLineLength, maxLineGap)
		# if not lines is None:
		gates = []
		if lines is not None:
			for line1 in lines:
				line1 = TwoPointLine(line1[0])
				cv2.line(lines_frame, (line1.x1, line1.y1),
					(line1.x2, line1.y2), (0, 0, 255), 3)
				if not self.__possible_line(line1):
					continue
				for line2 in lines:
					line2 = TwoPointLine(line2[0])
					if not self.__possible_line(line2):
						continue
					gates.append((line1, line2))

		x = 0
		y = 0
		width = -1
		if gates:
			gates.sort(key=self.__possible_gate, reverse=True)
			gate = gates[0]
			score = self.__possible_gate(gate)
			if score > 0.2:
				line1, line2 = gate
				x = (line1.x1 + line1.x2 + line2.x1 + line2.x2) / 4 - (frame.shape[1] // 2)
				y = (line1.y1 + line1.y2 + line2.y1 + line2.y2) / 4 - (frame.shape[0] // 2)
				width = abs((line1.x1 + line1.x2) - (line2.x1 + line2.x2)) / 2
				cv2.line(
					results_frame,
					(line1.x1, line1.y1),
					(line1.x2, line1.y2), (0, 255 - int(score * 255), int(score * 255)), 3)
				cv2.line(
					results_frame,
					(line2.x1, line2.y1),
					(line2.x2, line2.y2), (0, 255 - int(score * 255), int(score * 255)), 3)
		return (x, y, width, [blurred, edges, lines_frame, results_frame])


def main(args=None):
	rclpy.init(args=args)
	gate_tracker = GateTrackerNode()
	rclpy.spin(gate_tracker)

if __name__ == '__main__':
	main()
