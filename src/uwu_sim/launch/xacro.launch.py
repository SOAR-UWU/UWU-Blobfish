"""Launch file to compile robot's xacro and other robot things."""

from ament_index_python.packages import get_package_share_path
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    # LogInfo,
)
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution

ROBOT_TYPE = "blobsimp"
ROBOT_XACRO_NAME = "model.sdf.xacro"
ROBOT_SDF_NAME = "model.sdf"


def declare_launch_arguments():
    """Documentation of available arguments go here."""
    robot_type = DeclareLaunchArgument("robot", default_value=ROBOT_TYPE)
    return [robot_type]


def generate_launch_description():
    pkg_uwu_sim = get_package_share_path("uwu_sim")
    arg_robot_type = LaunchConfiguration("robot")

    # Reads stdout from xacro
    stdout_xacro = Command(
        [
            "xacro ",
            PathJoinSubstitution(
                [str(pkg_uwu_sim / "robots"), arg_robot_type, ROBOT_XACRO_NAME]
            ),
        ]
    )

    # Write out the xacro file to update it
    write_xacro = ExecuteProcess(
        name="write_xacro",
        cmd=[
            "echo",
            ["'", stdout_xacro, "'"],
            ">",
            PathJoinSubstitution(
                [str(pkg_uwu_sim / "robots"), arg_robot_type, ROBOT_SDF_NAME]
            ),
        ],
        shell=True,
    )

    return LaunchDescription(
        [
            *declare_launch_arguments(),
            write_xacro,
            # LogInfo(msg=xacro_cmd),
        ]
    )
