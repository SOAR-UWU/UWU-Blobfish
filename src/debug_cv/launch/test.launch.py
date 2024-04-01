import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import (
    AnyLaunchDescriptionSource,
    PythonLaunchDescriptionSource,
)


def generate_launch_description():
    foxglove_pkg = get_package_share_directory("foxglove_bridge")
    cv_pkg = get_package_share_directory("blobfish_cv")

    foxglove_launch_dir = os.path.join(foxglove_pkg, "launch")
    foxglove_launch = IncludeLaunchDescription(
        AnyLaunchDescriptionSource(
            os.path.join(foxglove_launch_dir, "foxglove_bridge_launch.xml")
        )
    )
    cv_launch_dir = os.path.join(cv_pkg, "launch")
    cv_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(cv_launch_dir, "cv.launch.py"))
    )

    ld = LaunchDescription()
    ld.add_action(foxglove_launch)
    ld.add_action(cv_launch)
    return ld
