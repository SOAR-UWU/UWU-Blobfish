import os
import sys
from sys import executable

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

hardware_available = True

for arg in sys.argv:
    if arg == 'hardware_available:=false':
        hardware_available = False

def generate_launch_description():

    # Include vectornav launch file
    vn_pkg = get_package_share_directory('vectornav')
    vn_launch_dir = os.path.join(vn_pkg, 'launch')
    vn_launch = IncludeLaunchDescription(
      PythonLaunchDescriptionSource(os.path.join(vn_launch_dir, 'vectornav.launch.py'))
    )

    pid_configs = os.path.join(get_package_share_directory('pid_package'), 'config', "params.yaml")
    arduino_configs = os.path.join(get_package_share_directory('arduino_bridge'), 'config', "params.yaml")
    thruster_manager_configs = os.path.join(get_package_share_directory('thruster_manager'), 'config', "params.yaml")

    # pid node
    pid_node = Node(
        package="pid_package",
        executable="pid_node",
        parameters=[pid_configs]
    )

    pid_calibration = Node(
        package="pid_package",
        executable="offset_calibrator",
        parameters=[pid_configs]
    )

    pid_motor_dir_control = Node(
        package="pid_package",
        executable="motor_dir_control_node",
        parameters=[pid_configs]
    )

    thruster_manager_node = Node(
        package="thruster_manager",
        executable="thruster_manager",
        parameters=[thruster_manager_configs]
    )

    motor_bridge = Node(
        package="arduino_bridge",
        executable="bridge",
        parameters=[arduino_configs]
    )

    # Create the launch description and populate
    # if hardware is not available, do not attempt to launch the IMU and Arduino nodes
    ld = LaunchDescription()
    if hardware_available:
        ld.add_action(vn_launch)
        ld.add_action(motor_bridge)
    ld.add_action(pid_calibration)
    ld.add_action(pid_node)
    ld.add_action(pid_motor_dir_control)
    ld.add_action(thruster_manager_node)
    return ld
