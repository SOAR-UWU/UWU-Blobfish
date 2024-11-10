import os
import sys

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

hardware_available = True

for arg in sys.argv:
    if arg == 'hardware_available:=false':
        hardware_available = False

def generate_launch_description():

    pid_pkg = get_package_share_directory('blobfish_pid')
    thruster_pkg = get_package_share_directory('blobfish_thrusters')
    arduino_pkg = get_package_share_directory('arduino_bridge')
    sensors_pkg = get_package_share_directory('blobfish_sensors')
    cv_pkg = get_package_share_directory('blobfish_cv')

    pid_launch_dir = os.path.join(pid_pkg, 'launch')
    pid_launch = IncludeLaunchDescription(
      PythonLaunchDescriptionSource(os.path.join(pid_launch_dir, 'pid_launch.py'))
    )

    thruster_launch_dir = os.path.join(thruster_pkg, 'launch')
    thruster_launch = IncludeLaunchDescription(
      PythonLaunchDescriptionSource(os.path.join(thruster_launch_dir, 'thruster_manager_launch.py'))
    )

    arduino_launch_dir = os.path.join(arduino_pkg, 'launch')
    arduino_launch = IncludeLaunchDescription(
      PythonLaunchDescriptionSource(os.path.join(arduino_launch_dir, 'arduino_launch.py'))
    )

    sensors_launch_dir = os.path.join(sensors_pkg, 'launch')
    sensors_launch = IncludeLaunchDescription(
      PythonLaunchDescriptionSource(os.path.join(sensors_launch_dir, 'imu_publisher_launch.py'))
    )

    cv_launch_dir = os.path.join(cv_pkg, 'launch')
    cv_launch = IncludeLaunchDescription(
      PythonLaunchDescriptionSource(os.path.join(cv_launch_dir, 'cv.launch.py'))
    )

    # Create the launch description and populate
    # if hardware is not available, do not attempt to launch the IMU and Arduino nodes
    ld = LaunchDescription()
    if hardware_available:
        ld.add_action(arduino_launch)
        ld.add_action(sensors_launch)
        ld.add_action(cv_launch)
    ld.add_action(pid_launch)
    ld.add_action(thruster_launch)
    return ld
