from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, GroupAction
from launch_ros.actions import Node, PushRosNamespace
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
  ld = LaunchDescription()

  # declare launch variables
  ns = "beluga_cv"
  robot_ns = "beluga"

  beluga_cv_pkg_name = 'beluga_cv'

  launch_cv_as_group = GroupAction(
    actions = [
      Node(
        package=beluga_cv_pkg_name, 
        executable='flare_tracker.py'
      ),
      Node(
        package=beluga_cv_pkg_name, 
        executable='gate_tracker.py'
      )
    ]
  )
  ld.add_action(launch_cv_as_group)
  
  return ld