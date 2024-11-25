from ament_index_python.packages import get_package_share_path
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    pkg_this = get_package_share_path("blobfish_control")

    exe = Node(
        package="blobfish_control",
        executable="routine",
        parameters=[{"config_path": str(pkg_this / "config" / "routine.yaml")}],
    )

    ld = LaunchDescription()
    ld.add_action(exe)
    return ld
