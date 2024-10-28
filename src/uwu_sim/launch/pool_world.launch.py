"""Launch file for pool world.

Refer to https://docs.ros.org/en/humble/p/launch/user_docs/source/architecture.html
for list of available launch functions.
"""

from ament_index_python.packages import get_package_share_path
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    IncludeLaunchDescription,
    # LogInfo,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    Command,
    LaunchConfiguration,
    PathJoinSubstitution,
)

WORLD_SDF = "pool_world.sdf"
ROBOT_TYPE = "blobsimp"
ROBOT_XACRO_NAME = "model.sdf.xacro"
ROBOT_SDF_NAME = "model.sdf"


def declare_launch_arguments():
    """Documentation of available arguments go here."""
    world_sdf = DeclareLaunchArgument("world_sdf", default_value=WORLD_SDF)
    robot_type = DeclareLaunchArgument("robot", default_value=ROBOT_TYPE)
    return [world_sdf, robot_type]


def generate_launch_description():
    # Package share path
    pkg_ros_gz_sim = get_package_share_path("ros_gz_sim")
    pkg_uwu_sim = get_package_share_path("uwu_sim")

    # Retrieve arguments
    arg_world_sdf = LaunchConfiguration("world_sdf")
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

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            str(pkg_ros_gz_sim / "launch" / "gz_sim.launch.py")
        ),
        launch_arguments={"gz_args": ["-r ", arg_world_sdf]}.items(),
    )

    return LaunchDescription(
        [
            *declare_launch_arguments(),
            write_xacro,
            # LogInfo(msg=xacro_cmd),
            gazebo,
        ]
    )
