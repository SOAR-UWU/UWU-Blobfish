from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, GroupAction
from launch_ros.actions import Node, PushRosNamespace
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
  ld = LaunchDescription()

  # declare launch variables
  ns = "beluga_pid"
  robot_ns = "beluga"
  state_ns = "beluga_state"

  beluga_pid_pkg_name = 'beluga_pid'

  launch_pid_as_group = GroupAction(
    actions = [
      Node(
        package=beluga_pid_pkg_name, 
        executable='beluga_pid.py'
      )
    ]
  )
  ld.add_action(launch_pid_as_group)
  
  return ld

