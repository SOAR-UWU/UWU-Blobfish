"""Launch file for testing motors and figuring out motor order."""

from ament_index_python.packages import get_package_share_path
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    pkg_arduino = get_package_share_path("arduino_bridge")
    pkg_thruster = get_package_share_path("blobfish_thrusters")
    pkg_this = get_package_share_path("diagnostics")

    arduino = IncludeLaunchDescription(
        str(pkg_arduino / "launch" / "arduino_launch.py")
    )

    thruster = IncludeLaunchDescription(
        str(pkg_thruster / "launch" / "thruster_manager_launch.py")
    )

    motor_node = Node(
        package="diagnostics",
        executable="motor",
        parameters=[{"config_path": str(pkg_this / "config" / "motor.yaml")}],
    )

    ld = LaunchDescription()
    ld.add_action(arduino)
    ld.add_action(thruster)
    ld.add_action(motor_node)
    return ld
