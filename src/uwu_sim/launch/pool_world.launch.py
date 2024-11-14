"""Launch file for pool world. Add any pool world specific nodes here.

Refer to https://docs.ros.org/en/humble/p/launch/user_docs/source/architecture.html
for list of available launch functions.
"""

from ament_index_python.packages import get_package_share_path
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration

WORLD_SDF = "world_pool.sdf"
GZ_DEBUG = False


def declare_launch_arguments():
    """Documentation of available arguments go here."""
    world_sdf = DeclareLaunchArgument("world_sdf", default_value=WORLD_SDF)
    return [world_sdf]


def generate_launch_description():
    pkg_ros_gz_sim = get_package_share_path("ros_gz_sim")
    arg_world_sdf = LaunchConfiguration("world_sdf")

    gazebo = IncludeLaunchDescription(
        str(pkg_ros_gz_sim / "launch" / "gz_sim.launch.py"),
        launch_arguments={
            "gz_args": [arg_world_sdf, f" -v{'4' if GZ_DEBUG else '0'}"]
        }.items(),
    )

    return LaunchDescription([*declare_launch_arguments(), gazebo])
