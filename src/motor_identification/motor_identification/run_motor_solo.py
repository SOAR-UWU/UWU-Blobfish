import rclpy
from rclpy.node import Node
from std_msgs.msg import Char
from rclpy.parameter import Parameter
from blobfish_msgs.msg import Motors

class SoloMotorNode(Node):
    def __init__(self):
        super().__init__("solo_motor_node")

        self.declare_parameter("motor_value", 1500)
        self.motor_pub = self.create_publisher(Motors, "blobfish/motor_values", 10)
        self.create_subscription(Char, "/keypress", self.track_keypresses, 10)
        self.current_motor = 1
        self.publish_motor_params()
        self.get_logger().info("solo motor node started")

    def publish_motor_params(self):
        msg = Motors()
        msg.motor_1 = 1500
        msg.motor_2 = 1500
        msg.motor_3 = 1500
        msg.motor_4 = 1500
        msg.motor_5 = 1500
        msg.motor_6 = 1500
        msg.motor_7 = 1500
        active_motor_name = "motor_" + str(self.current_motor)
        msg.__setattr__(active_motor_name, self.get_parameter("motor_value").value)
        self.motor_pub.publish(msg)

    def track_keypresses(self, msg):
        keypress = chr(msg.data)
        if keypress in "1234567":
            self.current_motor = int(keypress)
            self.get_logger().info("Tuning motor " + str(self.current_motor))
            new_param = rclpy.parameter.Parameter(
                "motor_value",
                rclpy.Parameter.Type.INTEGER,
                1500
            )
            self.set_parameters([new_param])
            self.get_logger().info("Current motor " + str(self.current_motor) + " value: " + str(self.get_parameter("motor_value").value))
        if keypress in ",.":
            param_val = self.get_parameter("motor_value").value
            if keypress == ",":
                param_val -= 50
            else:
                param_val += 50
            new_param = rclpy.parameter.Parameter(
                "motor_value",
                rclpy.Parameter.Type.INTEGER,
                param_val
            )
            self.set_parameters([new_param])
            self.get_logger().info("Current motor value: " + str(self.get_parameter("motor_value").value))
            self.publish_motor_params()
        if keypress in "hH":
            self.get_logger().info("Help:")
            self.get_logger().info("1-7 - Run motor 1-7")
            self.get_logger().info(", - Decrease")
            self.get_logger().info(". - Increase")
            self.get_logger().info("Current motor value " + str(self.current_motor) + ": " + str(self.get_parameter("motor_value").value))
            self.get_logger().info("Current motor: " + str(self.current_motor))

def main():
    rclpy.init()
    node = SoloMotorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()