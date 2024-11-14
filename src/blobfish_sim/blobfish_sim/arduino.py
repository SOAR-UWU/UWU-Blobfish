"""Replicate `arduino_bridge/arduino_listener.py`.

Note that the depth sensor isn't implemented here like in the original node.
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from std_msgs.msg import Float64

from blobfish_msgs.msg import Motors, MotorsFloat

NODE_NAME = "sim_arduino_bridge"
ROS_TOPIC = "/blobfish/motor_values"
# See `uwu_sim/robots/blobsimp/model.sdf.xacro`, specifically the `gz-sim-thruster-system`
# plugin for more info.
GZ_TOPICS = dict(
    FL="/gz/blobfish/thruster/FL",
    FR="/gz/blobfish/thruster/FR",
    ML="/gz/blobfish/thruster/ML",
    MR="/gz/blobfish/thruster/MR",
    BL="/gz/blobfish/thruster/BL",
    BR="/gz/blobfish/thruster/BR",
    BM="/gz/blobfish/thruster/BM",
)

# TODO: When we fixed the cursed motor order either by improving the Arduino or wiring,
# we can remove this:
MOTOR_ORDER = [None, "BM", "MR", "FL", "ML", "BL", "BR", "FR"]

# See: https://bluerobotics.com/store/thrusters/t100-t200-thrusters/t200-thruster-r2-rp/
# Ultimately, there's no reason to use the real values, but why not?
# I'll assume nominal voltage values.
# Values are in kg*f, 1 kg*f = 9.80665N. Gazebo uses N.
KG_F_TO_N = 9.80665
MIN_THURST = 0.02 * KG_F_TO_N
MAX_FWD_THRUST = 5.25 * KG_F_TO_N
MAX_REV_THRUST = 4.1 * KG_F_TO_N
THRUST_RESCALE = 1  # Account for simulation robot weight & drag being different.

# See: https://bluerobotics.com/store/thrusters/speed-controllers/besc30-r3/
# As a convention born of practicality, most ESCs use servo control signals.
# These are passed to Arduino's Servo.writeMicroseconds(). Values are gotten from
# the technical details in the link above.
SERVO_NEUTRAL = 1500
SERVO_DEADBAND = 25
SERVO_FULL_REV = 1100
SERVO_FULL_FWD = 1900


class SimArduinoBridge(Node):
    """Send motor values to the Arduino (simulated)."""

    def __init__(self):
        super(SimArduinoBridge, self).__init__(NODE_NAME)
        self.create_subscription(
            Motors, ROS_TOPIC, self.callback, qos_profile_sensor_data
        )
        self.__pubs = {
            k: self.create_publisher(Float64, v, 0) for k, v in GZ_TOPICS.items()
        }
        self.__debug_pub = self.create_publisher(
            MotorsFloat, "/blobfish/motor_floats", 0
        )

    def _map_motor_order(self, msg: Motors):
        vals = {}
        vals[MOTOR_ORDER[1]] = msg.motor_1
        vals[MOTOR_ORDER[2]] = msg.motor_2
        vals[MOTOR_ORDER[3]] = msg.motor_3
        vals[MOTOR_ORDER[4]] = msg.motor_4
        vals[MOTOR_ORDER[5]] = msg.motor_5
        vals[MOTOR_ORDER[6]] = msg.motor_6
        vals[MOTOR_ORDER[7]] = msg.motor_7
        return vals

    def _map_val_to_float(self, motors: dict):
        out = {}
        for motor, val in motors.items():
            # Clamp to valid range.
            val = min(max(val, SERVO_FULL_REV), SERVO_FULL_FWD)
            # 0 if within deadband.
            if abs(val - SERVO_NEUTRAL) <= SERVO_DEADBAND:
                val = 0.0
            # Calculate negative thrust.
            elif val < SERVO_NEUTRAL:
                val = (val - SERVO_NEUTRAL) / (SERVO_NEUTRAL - SERVO_FULL_REV)
            # Calculate positive thrust.
            elif val > SERVO_NEUTRAL:
                val = (val - SERVO_NEUTRAL) / (SERVO_FULL_FWD - SERVO_NEUTRAL)
            else:
                raise ValueError(f"Invalid servo value: {val}")
            out[motor] = val
        return out

    def _map_float_to_thrust(self, motors: dict):
        out = {}
        for motor, val in motors.items():
            val *= MAX_FWD_THRUST if val > 0 else MAX_REV_THRUST
            val = 0.0 if abs(val) < MIN_THURST else val
            out[motor] = val * THRUST_RESCALE
        return out

    def callback(self, msg: Motors):
        vals = self._map_motor_order(msg)
        vals = self._map_val_to_float(vals)
        self.__debug_pub.publish(MotorsFloat(**{k.lower(): v for k, v in vals.items()}))
        vals = self._map_float_to_thrust(vals)
        # NOTE: Best way to see how motors respond is to comment out below pub loop.
        for motor, pub in self.__pubs.items():
            pub.publish(Float64(data=float(vals[motor])))


def main(args=None):
    rclpy.init(args=args)
    node = SimArduinoBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
