import os
from sys import executable

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():

    # Include vectornav launch file
    vn_pkg = get_package_share_directory('vectornav')
    vn_launch_dir = os.path.join(vn_pkg, 'launch')
    vn_launch = IncludeLaunchDescription(
      PythonLaunchDescriptionSource(os.path.join(vn_launch_dir, 'vectornav.launch.py'))
    )

    # pid node
    pid_node = Node(
        package="pid_package",
        executable="pid_node"
    )

    pid_calibration = Node(
        package="pid_package",
        executable="offset_calibrator"
    )

    thruster_manager_node = Node(
        package="thruster_manager",
        executable="thruster_manager"
    )

    motor_bridge = Node(
        package="arduino_bridge",
        executable="bridge"
    )

    # Create the launch description and populate
    ld = LaunchDescription()
    ld.add_action(vn_launch)
    ld.add_action(pid_calibration)
    ld.add_action(pid_node)
    ld.add_action(thruster_manager_node)
    ld.add_action(motor_bridge)
    return ld
