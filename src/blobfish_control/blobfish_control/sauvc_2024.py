#!/usr/bin/env python3
import rclpy
import smach
import time
import math
from .base_strategy import BaseStrategyNode
from rclpy.node import Node
from std_msgs.msg import String, Float64
from geometry_msgs.msg import Twist, Pose2D
from vision_msgs.msg import BoundingBox2D

class FinalRoundStrategyNode(BaseStrategyNode):
    class SearchGate(smach.State):
        def __init__(self, outer: BaseStrategyNode):
            smach.State.__init__(self, outcomes=['found_gate', 'time_out'])
            self.outer = outer
            self.status_pub = self.outer.create_publisher(String, 'status', 10)

        def execute(self, userdata):
            # # rate = FinalRoundStrategyNode.create_rate(frequency=1)
            start_time = time.time()
            while rclpy.ok():
                self.outer.output.speed = 0.8
                self.outer.output.target_yaw = self.outer.input.initial_yaw
                self.outer.output.target_depth = 1

                if self.outer.input.gate_pos.size_y > 0:
                    status = String()
                    status.data = 'TrackGate'
                    self.status_pub.publish(status)
                    return 'found_gate'

                if time.time() - start_time > 10:
                    return 'time_out'

                # rate.sleep()

    class TrackGate(smach.State):
        def __init__(self, outer: BaseStrategyNode):
            smach.State.__init__(self, outcomes=['lost_target', 'passed_gate'])
            self.outer = outer
            self.status_pub = self.outer.create_publisher(String, 'status', 10)

        def execute(self, userdata):
            # rate = FinalRoundStrategyNode.create_rate(frequency=1)
            while rclpy.ok():
                gate_pose = self.outer.input.gate_pos
                flare_pose = self.outer.input.flare_pos
                image_size_x = self.outer.input.image_size_x 
                image_size_y = self.outer.input.image_size_y

                if flare_pose.size_x > 5:
                    print('flare_detected.')

                if gate_pose.size_x < 0:
                    return 'lost_target'

                if gate_pose.size_x > 350:
                    status = String()
                    status.data = 'PassGate'
                    self.status_pub.publish(status)
                    return 'passed_gate'

                self.outer.output.speed = 0.8
                testA = gate_pose.center.position.x
                testB = flare_pose.center.position.x
                if flare_pose.center.position.x >= gate_pose.center.position.x:    
                    self.outer.output.target_yaw = self.outer.input.current_yaw - (0.001 * gate_pose.center.position.x) + (0.2 * (abs(image_size_x - flare_pose.center.position.x)))
                elif flare_pose.center.position.x < gate_pose.center.position.x: 
                    self.outer.output.target_yaw = self.outer.input.current_yaw - (0.001 * gate_pose.center.position.x) - (0.2 * (abs(flare_pose.center.position.x)))
                self.outer.output.target_depth = 1

                # rate.sleep()

    class PassGate(smach.State):
        def __init__(self, outer: BaseStrategyNode):
            smach.State.__init__(self, outcomes=['finished'])
            self.outer = outer
            self.status_pub = self.outer.create_publisher(String, 'status', 10)

        def execute(self, userdata):
            # rate = FinalRoundStrategyNode.create_rate(frequency=1)
            start_time = time.time()
            while rclpy.ok():
                gate_pose = self.outer.input.gate_pos

                self.outer.output.speed = 0.8
                if gate_pose.size_x < 0:
                    self.outer.output.target_yaw = self.outer.input.initial_yaw
                else:
                    self.outer.output.current_yaw = \
                        self.outer.input.current_yaw - 0.001 * gate_pose.center.position.x
                self.outer.output.target_depth = 1

                if time.time() - start_time > 15:
                    status = String()
                    status.data = 'LeaveGate'
                    self.status_pub.publish(status)
                    return 'finished'

                # rate.sleep()

    class LeaveGate(smach.State):
        def __init__(self, outer: BaseStrategyNode):
            smach.State.__init__(self, outcomes=['finished'])
            self.outer = outer
            self.status_pub = self.outer.create_publisher(String, 'status', 10)

        def execute(self, userdata):
            # rate = FinalRoundStrategyNode.create_rate(frequency=1)
            start_time = time.time()
            while rclpy.ok():
                self.outer.output.speed = 0.8
                self.outer.output.target_yaw = 0.85
                self.outer.output.target_depth = 1

                if time.time() - start_time > 10:
                    status = String()
                    status.data = 'LeaveGate'
                    self.status_pub.publish(status)
                    return 'finished'

                # rate.sleep()

    class SearchFlare(smach.State):
        def __init__(self, outer: BaseStrategyNode):
            smach.State.__init__(self, outcomes=['found_flare', 'time_out'])
            self.outer = outer
            self.status_pub = self.outer.create_publisher(String, 'status', 10)

        def execute(self, userdata):
            # rate = FinalRoundStrategyNode.create_rate(frequency=1)
            start_time = time.time()
            while rclpy.ok():
                self.outer.output.speed = 0.8
                self.outer.output.target_yaw = \
                    0.85 + 0.4 * math.sin(time.time())
                self.outer.output.target_depth = 1.3

                if self.outer.input.flare_pos.size_x > 0:
                    status = String()
                    status.data = 'TrackFlare'
                    self.status_pub.publish(status)
                    return 'found_flare'

                if time.time() - start_time > 50:
                    return 'time_out'

                # rate.sleep()

    class TrackFlare(smach.State):
        def __init__(self, outer: BaseStrategyNode):
            smach.State.__init__(self, outcomes=['lost_target', 'close_enough'])
            self.outer = outer
            self.status_pub = self.outer.create_publisher(String, 'status', 10)

        def execute(self, userdata):
            # rate = FinalRoundStrategyNode.create_rate(frequency=1)
            while rclpy.ok():
                flare_pos = self.outer.input.flare_pos

                if flare_pos.size_x < 0:
                    status = String()
                    status.data = 'SearchFlare'
                    self.status_pub.publish(status)
                    return 'lost_target'

                if flare_pos.size_x > 100:
                    status = String()
                    status.data = 'HitFlare'
                    self.status_pub.publish(status)
                    return 'close_enough'

                self.outer.output.speed = 0.8
                self.outer.output.target_yaw = \
                    self.outer.input.current_yaw + 0.001 * flare_pos.center.position.x
                self.outer.output.target_depth = 1.3

                # rate.sleep()

    class HitFlare(smach.State):
        def __init__(self, outer: BaseStrategyNode):
            smach.State.__init__(self, outcomes=['finished'])
            self.outer = outer
            self.status_pub = self.outer.create_publisher(String, 'status', 10)

        def execute(self, userdata):
            # rate = FinalRoundStrategyNode.create_rate(frequency=1)
            start_time = time.time()
            while rclpy.ok():
                flare_pos = self.outer.input.flare_pos

                if flare_pos.size_x > 0:
                    self.outer.output.target_yaw = \
                        self.outer.input.current_yaw - 0.001 * flare_pos.center.position.x
                else:
                    self.outer.output.target_yaw = \
                        0.95 + 0.26 * math.sin(time.time())

                self.outer.output.speed = 0.8
                self.outer.output.target_depth = 1.3

                if time.time() - start_time > 20:
                    status = String()
                    status.data = 'Surfacing'
                    self.status_pub.publish(status)
                    return 'finished'

                # rate.sleep()

    class Surfacing(smach.State):
        def __init__(self, outer: BaseStrategyNode):
            smach.State.__init__(self, outcomes=['finished'])
            self.outer = outer
            self.status_pub = self.outer.create_publisher(String, 'status', 10)

        def execute(self, userdata):
            # rate = FinalRoundStrategyNode.create_rate(frequency=1)
            start_time = time.time()
            while time.time() - start_time < 20 and (rclpy.ok()):
                status = String()
                status.data = 'Succeeded'
                self.outer.output.speed = 0
                self.outer.output.target_yaw = 2.1
                self.outer.output.target_depth = 0
                # rate.sleep()
                self.status_pub.publish(status)
            return 'finished'

    def __init__(self):
        self.current_status = ''
        super().__init__(outcomes=['succeeded'])
        self.status_pub = self.create_publisher(String, 'status', 10)
        with self.sm:
            smach.StateMachine.add(
                'SearchGate', self.SearchGate(self),
                transitions={
                    'found_gate': 'TrackGate',
                    'time_out': 'PassGate'
                })

            smach.StateMachine.add(
                'TrackGate', self.TrackGate(self),
                transitions={
                    'lost_target': 'SearchGate',
                    'passed_gate': 'PassGate'
                }
            )

            smach.StateMachine.add(
                'PassGate', self.PassGate(self),
                transitions={
                    'finished': 'LeaveGate'
                }
            )

            smach.StateMachine.add(
                'LeaveGate', self.LeaveGate(self),
                transitions={
                    'finished': 'SearchFlare'
                }
            )

            smach.StateMachine.add(
                'SearchFlare', self.SearchFlare(self),
                transitions={
                    'found_flare': 'TrackFlare',
                    'time_out': 'Surfacing'
                })

            smach.StateMachine.add(
                'TrackFlare', self.TrackFlare(self),
                transitions={
                    'lost_target': 'SearchFlare',
                    'close_enough': 'HitFlare'
                }
            )

            smach.StateMachine.add(
                'HitFlare', self.HitFlare(self),
                transitions={
                    'finished': 'Surfacing'
                }
            )

            smach.StateMachine.add(
                'Surfacing', self.Surfacing(self),
                transitions={
                    'finished': 'succeeded'
                }
            )

def main(args=None):
    rclpy.init(args=args)
    final_strategy = FinalRoundStrategyNode()
    final_strategy.execute()
    rclpy.spin(final_strategy)

if __name__ == '__main__':
    main()