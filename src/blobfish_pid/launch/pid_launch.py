from ament_index_python.packages import get_package_share_path
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    pkg_blobfish_pid = get_package_share_path("blobfish_pid")

    pid_node = Node(
        package="blobfish_pid",
        executable="pid_node",
        parameters=[{"config_path": str(pkg_blobfish_pid / "config" / "pid.yaml")}],
    )

    # Create the launch description and populate
    ld = LaunchDescription()
    ld.add_action(pid_node)
    return ld
