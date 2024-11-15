from ament_index_python.packages import get_package_share_path
from launch import LaunchDescription
from launch.actions import LogInfo
from launch_ros.actions import Node
from serial.tools import list_ports
from serial.tools.list_ports_common import ListPortInfo

VN_DEV_ID = "0403:6001"


def generate_launch_description():
    pkg_this = get_package_share_path("blobfish_sensors")

    try:
        dev: ListPortInfo = next(list_ports.grep(VN_DEV_ID))
    except StopIteration:
        return LaunchDescription([LogInfo(msg="IMU not found, skipping...")])

    vn_node = Node(
        package="vectornav",
        executable="vectornav",
        parameters=[
            str(pkg_this / "config" / "vectornav.yaml"),
            # str(pkg_this / "config" / "vn_100_800hz.yaml"),
            {"port": dev.device},
        ],
    )

    vn_msg_node = Node(
        package="vectornav",
        executable="vn_sensor_msgs",
        parameters=[str(pkg_this / "config" / "vectornav.yaml")],
    )

    imu_node = Node(
        package="blobfish_sensors",
        # executable="imu_publisher",
        executable="imu_v2",
        parameters=[str(pkg_this / "config" / "params.yaml")],
    )

    ld = LaunchDescription()
    ld.add_action(LogInfo(msg=f"IMU found: {dev.device}"))
    ld.add_action(vn_node)
    # ld.add_action(vn_msg_node)
    ld.add_action(imu_node)
    return ld
