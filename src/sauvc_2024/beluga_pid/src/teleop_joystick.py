#!/usr/bin/env python3
import rospy
from std_msgs.msg import Float64
from sensor_msgs.msg import Joy


class TeleopNode:
    def __init__(self):
        rospy.init_node('teleop')

        yaw_pub = rospy.Publisher('yaw', Float64, queue_size=10)
        pitch_pub = rospy.Publisher('pitch', Float64, queue_size=10)
        roll_pub = rospy.Publisher('roll', Float64, queue_size=10)
        depth_pub = rospy.Publisher('depth', Float64, queue_size=10)
        speed_pub = rospy.Publisher('speed', Float64, queue_size=10)

        self.last_joy_axes = [0] * 6
        rospy.Subscriber('/joy', Joy, self.joy_callback)

        depth = 1.0
        yaw = 2.0
        rate = rospy.Rate(100)
        while not rospy.is_shutdown():
            depth += 0.003 * (self.last_joy_axes[2] - self.last_joy_axes[5])
            depth_pub.publish(Float64(depth))
            yaw += 0.003 * (self.last_joy_axes[0])
            yaw_pub.publish(Float64(yaw))
            speed_pub.publish(self.last_joy_axes[1])
            pitch_pub.publish(self.last_joy_axes[4])
            roll_pub.publish(-self.last_joy_axes[3])

            rate.sleep()

    def joy_callback(self, msg: Joy):
        self.last_joy_axes = msg.axes


if __name__ == "__main__":
    TeleopNode()
