# Author: Addison Sears-Collins
# Date: August 27, 2021
# Description: Launch a basic mobile robot URDF file using Rviz.
# https://automaticaddison.com

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
  ld = LaunchDescription()

  # declare launch variables
  beluga_pid_pkg_name = 'beluga_pid'
  beluga_control_pkg_name = 'beluga_control'
  beluga_cv_pkg_name = 'beluga_cv' 
  beluga_sensors_pkg_name = 'beluga_sensors'

  pkg_beluga_pid = FindPackageShare(package=beluga_pid_pkg_name).find(beluga_pid_pkg_name)
  pkg_beluga_sensors = FindPackageShare(package=beluga_sensors_pkg_name).find(beluga_sensors_pkg_name)
  pkg_beluga_cv = FindPackageShare(package=beluga_cv_pkg_name).find(beluga_cv_pkg_name)
   
  start_beluga_control_cmd = IncludeLaunchDescription(
    PathJoinSubstitution([pkg_beluga_pid, beluga_pid_pkg_name, 'beluga_pid.launch.py'])
  )
  ld.add_action(start_beluga_control_cmd)

  start_beluga_sensors_cmd = IncludeLaunchDescription(
    PathJoinSubstitution([pkg_beluga_sensors, beluga_sensors_pkg_name, 'state_publisher.launch.py'])
  )
  ld.add_action(start_beluga_sensors_cmd)

  start_beluga_cv_cmd = IncludeLaunchDescription(
    PathJoinSubstitution([pkg_beluga_cv, beluga_cv_pkg_name, 'launch_all.launch.py'])
  )
  ld.add_action(start_beluga_cv_cmd)

  return ld


