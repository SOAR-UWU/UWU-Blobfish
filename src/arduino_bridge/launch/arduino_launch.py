from ament_index_python.packages import get_package_share_path
from launch import LaunchDescription
from launch.actions import LogInfo
from launch_ros.actions import Node
from serial.tools import list_ports
from serial.tools.list_ports_common import ListPortInfo

ARDUINO_DEV_ID = "1a86:7523"


def generate_launch_description():
    pkg_this = get_package_share_path("arduino_bridge")

    # TODO: needs testing.
    try:
        dev: ListPortInfo = next(list_ports.grep(ARDUINO_DEV_ID))
    except StopIteration:
        return LaunchDescription([LogInfo(msg="Arduino not found, skipping...")])

    motor_bridge = Node(
        package="arduino_bridge",
        executable="bridge",
        parameters=[
            str(pkg_this / "config" / "params.yaml"),
            {"arduino_files": str(pkg_this / "arduino")},
            {"arduino_port": dev.device},
        ],
    )

    ld = LaunchDescription()
    ld.add_action(LogInfo(msg=f"Arduino found: {dev.device}"))
    ld.add_action(motor_bridge)
    return ld
