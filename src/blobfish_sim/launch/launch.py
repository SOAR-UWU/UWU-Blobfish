"""All simulator bridging nodes."""

from ament_index_python.packages import get_package_share_path
from launch import LaunchDescription
from launch_ros.actions import Node

THIS_NAME = "blobfish_sim"
# Position IMU emulates IMUs like VectorNav with built-in position dead reckoning.
USE_POS_IMU = False


def generate_launch_description():
    pkg_blobfish_sim = get_package_share_path(THIS_NAME)

    gz_topic_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        parameters=[{"config_file": str(pkg_blobfish_sim / "config" / "bridge.yaml")}],
    )
    keypress_bridge = Node(package=THIS_NAME, executable="sim_keypress")
    imu_bridge = Node(package=THIS_NAME, executable="sim_imu")
    pos_imu_bridge = Node(package=THIS_NAME, executable="sim_pos_imu")
    depth_bridge = Node(package=THIS_NAME, executable="sim_depth")
    arduino_bridge = Node(package=THIS_NAME, executable="sim_arduino")

    return LaunchDescription(
        [
            gz_topic_bridge,
            keypress_bridge,
            pos_imu_bridge if USE_POS_IMU else imu_bridge,
            depth_bridge,
            arduino_bridge,
        ]
    )
