from ament_index_python.packages import get_package_share_path
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    pkg_this = get_package_share_path("arduino_bridge")

    motor_bridge = Node(
        package="arduino_bridge",
        executable="bridge",
        parameters=[
            pkg_this / "config" / "params.yaml",
            {"arduino_files": str(pkg_this / "arduino")},
        ],
    )

    ld = LaunchDescription()
    ld.add_action(motor_bridge)
    return ld
