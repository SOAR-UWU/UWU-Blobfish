#!/usr/bin/env python3
import rospy
import numpy as np
from typing import Tuple
from std_msgs.msg import Float64
from geometry_msgs.msg import Twist


class PIDNode:
    def __init__(self):
        rospy.init_node('bubbles_pid')

        self.output = rospy.Publisher('control_effort', Twist, queue_size=10)

        self.control_vectors = []
        trans_matrix = np.identity(6)
        X, Y, Z, AX, AY, AZ = range(6)
        rospy.Subscriber('yaw/control_effort',   Float64, self.callback_factory(trans_matrix[AZ]))
        rospy.Subscriber('roll/control_effort', Float64, self.callback_factory(trans_matrix[AX]))
        rospy.Subscriber('pitch/control_effort',  Float64, self.callback_factory(trans_matrix[AY]))
        rospy.Subscriber('depth/control_effort', Float64, self.callback_factory(-trans_matrix[Z]))
        rospy.Subscriber('speed/setpoint',       Float64, self.callback_factory(trans_matrix[X]))

    def callback_factory(self, trans_vector: Tuple[float, float, float, float, float, float]):
        trans_vector = np.array(trans_vector)
        callback_id = len(self.control_vectors)
        self.control_vectors.append(0 * trans_vector)

        def pid_effort_callback(msg: Float64):
            self.control_vectors[callback_id] = msg.data * trans_vector
            self.publish_effort()

        return pid_effort_callback

    def publish_effort(self):
        final_vector = np.zeros(6)
        for v in self.control_vectors:
            final_vector += v
        cmd_vel = Twist()
        cmd_vel.linear.x = final_vector[0]
        cmd_vel.linear.y = final_vector[1]
        cmd_vel.linear.z = final_vector[2]
        cmd_vel.angular.x = final_vector[3]
        cmd_vel.angular.y = final_vector[4]
        cmd_vel.angular.z = final_vector[5]
        self.output.publish(cmd_vel)


if __name__ == "__main__":
    PIDNode()
    rospy.spin()
