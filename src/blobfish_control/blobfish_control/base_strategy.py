#!/usr/bin/env python3
import rclpy
import smach
import time
from rclpy.node import Node
from std_msgs.msg import Float64
from geometry_msgs.msg import Twist, Pose2D
from vision_msgs.msg import BoundingBox2D

#TO GO STRAIGHT

class Input:
    def __init__(self):
        self.current_yaw = 0
        self.current_depth = 0
        self.current_pitch = 0
        self.effective_roll = 0
        self.initial_yaw = 0
        self.initial_depth =  0
        self.initial_pitch = 0
        self.gate_pos = BoundingBox2D()
        self.flare_pos = BoundingBox2D()
        self.image_size_x = 640
        self.image_size_y = 480


class Output:
    def __init__(self, on_change_callback):
        self._speed = 0
        self._target_yaw = 0
        self._target_depth = 0
        self._target_pitch = 0
        self._on_change_callback = on_change_callback

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, new_speed):
        self._speed = new_speed
        self._on_change_callback()

    @property
    def target_yaw(self):
        return self._target_yaw

    @target_yaw.setter
    def target_yaw(self, new_target_yaw):
        self._target_yaw = new_target_yaw
        self._on_change_callback()

    @property
    def target_depth(self):
        return self._target_depth

    @target_depth.setter
    def target_depth(self, new_target_depth):
        self._target_depth = new_target_depth
        self._on_change_callback()

    @property
    def target_pitch(self):
        return self._target_pitch

    @target_pitch.setter
    def target_pitch(self, new_target_pitch):
        self._target_pitch = new_target_pitch
        self._on_change_callback()


class BaseStrategyNode(Node):
    def __init__(self, outcomes=[], input_keys=[], output_keys=[]):
        self.node_name = 'strategy'
        super().__init__(self.node_name)
        self.sm = smach.StateMachine(outcomes, input_keys, output_keys)

        self._output = Twist()

        try:
            import smach_ros
            sis = smach_ros.IntrospectionServer('server_name', self.sm, '/sm')
            sis.start()
        except Exception:
            pass

        self.input = Input()
        self.output = Output(self._on_output_update)

        self._setpoint_pub = self.create_publisher(Twist, 'blobfish/state_setpoints', 10)
        self._speed_setpoint_pub = self.create_publisher(Float64, 'blobfish/speed_setpoint', 10) 

        self._yaw_first_update = True
        self._depth_first_update = True
        self._pitch_first_update = True
        self.state_subscriber_ = self.create_subscription(Twist, 'blobfish/imu_measurements', self._on_state_update, 10)
        self.cv_gate_subscriber_ = self.create_subscription(BoundingBox2D, '/blobfish_cv/gate/pos', self._on_gate_pos_update, 10)
        self.cv_flare_subscriber_ = self.create_subscription(BoundingBox2D, '/blobfish_cv/flare/pos', self._on_flare_pos_update, 10)
        
        self._time_last_publish = 0

    def _on_state_update(self, msg):
        if self._state_first_update:
            self._state_first_update = False
            self.input.initial_yaw = msg.angular.z
            self.input.initial_depth = msg.linear.z
            self.input.initial_pitch = msg.angular.x
        self.input.current_yaw = msg.angular.z
        self.input.current_depth = msg.linear.z
        self.input.current_pitch = msg.angular.x

    def _on_gate_pos_update(self, msg):
        self.input.gate_pos = msg

    def _on_flare_pos_update(self, msg):
        self.input.flare_pos = msg

    def _on_output_update(self):
        if time.time() - self._time_last_publish > 0.01:
            self.effective_yaw = self.output.target_yaw
            self.effective_depth = self.output.target_depth
            self.effective_pitch = 0
            self.effective_roll = 0
            self._time_last_publish = time.time()

            self._output.angular.z = self.effective_yaw*1.0
            self._output.linear.z = self.effective_depth*1.0
            self._output.angular.y = self.effective_pitch*1.0
            self._output.angular.x = self.effective_roll*1.0
            
            #self._roll_pub.publish(Float64(0))
            speed = Float64()
            speed.data = 0.5
            self._setpoint_pub.publish(self._output)
            self._speed_setpoint_pub.publish(speed)

    def execute(self):
        return self.sm.execute()

def main(args=None):
    rclpy.init(args=args)
    strategy = BaseStrategyNode()
    rclpy.spin(strategy)

if __name__ == '__main__':
    main()
