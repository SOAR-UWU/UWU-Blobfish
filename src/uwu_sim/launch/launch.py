"""Main launch file for simulator.

Refer to https://docs.ros.org/en/humble/p/launch/user_docs/source/architecture.html
for list of available launch functions.
"""

from ament_index_python.packages import get_package_share_path
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription

WORLD_LAUNCH_FILE = "pool_world.launch.py"
ROBOT_TYPE = "blobsimp"


def generate_launch_description():
    pkg_uwu_sim = get_package_share_path("uwu_sim")
    pkg_blobfish_sim = get_package_share_path("blobfish_sim")

    xacro = IncludeLaunchDescription(
        str(pkg_uwu_sim / "launch" / "xacro.launch.py"),
        launch_arguments={"robot": ROBOT_TYPE}.items(),
    )
    world = IncludeLaunchDescription(str(pkg_uwu_sim / "launch" / WORLD_LAUNCH_FILE))
    bridge = IncludeLaunchDescription(str(pkg_blobfish_sim / "launch" / "launch.py"))
    robot = IncludeLaunchDescription(str(pkg_uwu_sim / "launch" / "robot.launch.py"))

    return LaunchDescription(
        [
            xacro,
            world,
            bridge,
            robot,
        ]
    )
