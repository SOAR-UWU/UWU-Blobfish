#!/usr/bin/env python3

import numpy as np
from typing import Sequence

import rclpy
from math import sin, pi
from geometry_msgs.msg import Twist, Vector3
from beluga_msgs.msg import Motors, MotorOffset
from uuv_gazebo_ros_plugins_msgs.msg import FloatStamped
from rclpy.node import Node
from rclpy.clock import Clock

class ThrusterManagerNode(Node):
	def __init__(self):
		self.node_name = 'thruster_manager'
		super().__init__(self.node_name) 
		
		# Do math
		theta = 45/180*pi
		self.transform_mat = np.array([
		#             x            y            z            r            p            h      
		[    sin(theta), -sin(theta),         0.0,         0.0,         0.0, -sin(theta)   ],          # left    front   motor
		[    sin(theta),  sin(theta),         0.0,         0.0,         0.0,  sin(theta)   ],          # right   front   motor
		[   -sin(theta), -sin(theta),         0.0,         0.0,         0.0,  sin(theta)   ],          # left    back    motor
		[   -sin(theta),  sin(theta),         0.0,         0.0,         0.0, -sin(theta)   ],          # right   back    motor
		[           0.0,         0.0,         1.0,        -1.0,         0.0,         0.0   ],          # left    middle  motor
		[           0.0,         0.0,         1.0,         1.0,         0.0,         0.0   ],          # right   middle  motor
		[           0.0,         0.0,         0.0,         0.0,        -1.0,         0.0   ],          # middle  back    motor
		])

		self.speed_x = 0.3
		self.scale = 300
		self.num_thrusters = len(self.transform_mat)
		self.motors = Motors()
		self.motors.motor_fl = 0
		self.motors.motor_fr = 0
		self.motors.motor_bl = 0
		self.motors.motor_br = 0
		self.motors.motor_ml = 0
		self.motors.motor_mr = 0
		self.motors.motor_bm = 0

		self.motor_publisher = self.create_publisher(Motors, '/motor_values', 10)
		self.twist_subscriber_ = self.create_subscription(Twist, '/beluga/control_effort', self.input_callback, 10)
		#self.vector_subscriber_ = self.create_subscription(Vector3, '/yawpitchroll_pid', self.input_callback, 10)
		#self.twist_subscriber_ = self.create_subscription(Twist, 'cmd_vel', self.input_callback, 10) ## for teleop node
		print("[Thruster Manager]: ThrusterManagerNode started")

	def input_callback(self, msg: Twist):
		control_vector = np.array([
			[   msg.linear.x   ],         # x
			[   msg.linear.y   ],         # y
			[   msg.linear.z   ],         # z
			[  msg.angular.x   ],         # r
			[  msg.angular.y   ],         # p
			[  msg.angular.z   ]          # h
		])
		output = (self.scale * self.transform_mat @ control_vector + 1500).clip(1200, 1800)
		self.motors.motor_fl = output[0]
		self.motors.motor_fr = output[1]
		self.motors.motor_bl = output[2]
		self.motors.motor_br = output[3]
		self.motors.motor_ml = output[4]
		self.motors.motor_mr = output[5]
		self.motors.motor_bm = output[6]
		self.motor_publisher.publish(self.motors)

	# def input_callback(self, msg: Vector3):
	# 	control_vector = np.array([
	# 		[   self.speed_x  ],  # x
	# 		[   0   ],            # y
	# 		[   0   ],            # z
	# 		[   msg.x   ],         # r
	# 		[   msg.y   ],         # p
	# 		[   msg.z   ]          # h
	# 	])
	# 	output = (self.scale * self.transform_mat @ control_vector + 1500).clip(1200, 1800)
	# 	self.motors.motor_fl = int(output[0])
	# 	self.motors.motor_fr = int(output[1])
	# 	self.motors.motor_bl = int(output[2])
	# 	self.motors.motor_br = int(output[3])
	# 	self.motors.motor_ml = int(output[4])
	# 	self.motors.motor_mr = int(output[5])
	# 	self.motors.motor_bm = int(output[6])
	# 	self.motor_publisher.publish(self.motors)

	def update_thrusters(self, output: Sequence[float]):
		for i in range(self.num_thrusters):
			self.thrusters[i].publish(output[i])

def main(args=None):
	rclpy.init(args=args)
	thruster_manager = ThrusterManagerNode()
	rclpy.spin(thruster_manager)

if __name__ == '__main__':
	main()
