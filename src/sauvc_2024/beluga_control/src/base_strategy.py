#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import smach
import time
from std_msgs.msg import Float64
from vision_msgs.msg import BoundingBox2D

#TO GO STRAIGHT

class Input:
    def __init__(self):
        self.current_yaw = 0
        self.current_depth = 0
        self.current_pitch = 0
        self.initial_yaw = 0
        self.initial_depth =  0
        self.initial_pitch = 0
        self.gate_pos = BoundingBox2D()
        self.flare_pos = BoundingBox2D()


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


class BaseStrategy(Node):
    def __init__(self, outcomes=[], input_keys=[], output_keys=[]):
        super().__init__('base_strategy')
        self.sm = smach.StateMachine(outcomes, input_keys, output_keys)

        try:
            import smach_ros
            sis = smach_ros.IntrospectionServer('server_name', self.sm, '/sm')
            sis.start()
        except Exception:
            pass

        self.input = Input()
        self.output = Output(self._on_output_update)

        self._roll_pub = self.create_publisher(Float64, '/beluga_pid/roll/setpoint', queue_size=10)
        self._pitch_pub = self.create_publisher(Float64, '/beluga_pid/pitch/setpoint', queue_size=10)
        self._yaw_pub = self.create_publisher(Float64, '/beluga_pid/yaw/setpoint', queue_size=10)
        self._depth_pub = self.create_publisher(Float64, '/beluga_pid/depth/setpoint', queue_size=10)
        self._speed_pub = self.create_publisher(Float64, '/beluga_pid/speed/setpoint', queue_size=10)

        self._yaw_first_update = True
        self._depth_first_update = True
        self._pitch_first_update = True
        self.create_subscrption('/beluga_state/yaw', Float64, self._on_yaw_update)
        self.create_subscrption('/beluga_state/depth', Float64, self._on_depth_update)
        self.create_subscrption('/beluga_state/pitch', Float64, self._on_pitch_update)
        self.create_subscrption('/beluga_cv/gate/pos', BoundingBox2D, self._on_gate_pos_update)
        self.create_subscrption('/beluga_cv/flare/pos', BoundingBox2D, self._on_flare_pos_update)

        self._time_last_publish = 0

    def _on_yaw_update(self, msg):
        if self._yaw_first_update:
            self._yaw_first_update = False
            self.input.initial_yaw = msg.data
        self.input.current_yaw = msg.data

    def _on_depth_update(self, msg):
        if self._depth_first_update:
            self._depth_first_update = False
            self.input.initial_depth = msg.data
        self.input.current_depth = msg.data

    def _on_pitch_update(self, msg):
        if self._pitch_first_update:
            self._pitch_first_update = False
            self.input.initial_pitch = msg.data
        self.input.current_pitch = msg.data

    def _on_gate_pos_update(self, msg):
        self.input.gate_pos = msg

    def _on_flare_pos_update(self, msg):
        self.input.flare_pos = msg

    def _on_output_update(self):

        if time.time() - self._time_last_publish > 0.01:
            self.effective_yaw = self.input.current_yaw - 0.0003 * self.input.gate_pos.center.x
            self.effective_depth = self.input.current_depth + 0.000125 * self.input.gate_pos.center.y
            self.effective_pitch = self.input.current_pitch + 0.0001 * self.input.gate_pos.center.y
            self._time_last_publish = time.time()
            #self._roll_pub.publish(Float64(0))
            self._pitch_pub.publish(Float64(0))
            self._yaw_pub.publish(Float64(self.effective_yaw))
            self._depth_pub.publish(Float64(1))
            self._speed_pub.publish(Float64(0.5))

    def execute(self):
        return self.sm.execute()
