"""Launch file for IRL robot nodes."""

from ament_index_python.packages import get_package_share_path
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription


def generate_launch_description():
    pkg_pid = get_package_share_path("blobfish_pid")
    pkg_thruster = get_package_share_path("blobfish_thrusters")
    pkg_cv = get_package_share_path("blobfish_cv")

    pid = IncludeLaunchDescription(str(pkg_pid / "launch" / "pid_launch.py"))
    thruster = IncludeLaunchDescription(
        str(pkg_thruster / "launch" / "thruster_manager_launch.py")
    )
    cv = IncludeLaunchDescription(str(pkg_cv / "launch" / "cv.launch.py"))

    return LaunchDescription(
        [
            # cv,
            pid,
            thruster,
        ]
    )
