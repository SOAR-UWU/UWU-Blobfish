import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    cam_cfg = os.path.join(
        get_package_share_directory("blobfish_cv"), "config", "params.yaml"
    )
    det_cfg = os.path.join(
        get_package_share_directory("blobfish_cv"), "config", "params.yaml"
    )
    cam_node = Node(
        package="usb_cam",
        executable="usb_cam_node_exe",
        parameters=[cam_cfg],
    )

    record_node = Node(package="debug_cv", executable="record_vid")

    cv_node1 = Node(
        package="blobfish_cv",
        executable="detect",
        remappings=[
            ("~/flare_bbox", "/blobfish_cv/flare/pos"),
        ],
        name="detect_flare",
        parameters=[det_cfg],
    )

    cv_node2 = Node(
        package="blobfish_cv",
        executable="detect",
        remappings=[
            ("~/gate_bbox", "/blobfish_cv/gate/pos"),
        ],
        name="detect_others",
        parameters=[det_cfg],
    )

    ld = LaunchDescription()
    ld.add_action(cam_node)
    ld.add_action(record_node)
    ld.add_action(cv_node1)
    ld.add_action(cv_node2)
    return ld
