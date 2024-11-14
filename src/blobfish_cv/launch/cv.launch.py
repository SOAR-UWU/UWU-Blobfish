from ament_index_python.packages import get_package_share_path
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    pkg_this = get_package_share_path("blobfish_cv")
    params_cam = pkg_this / "config" / "params.yaml"

    # cam_node = Node(
    #     package="usb_cam",
    #     executable="usb_cam_node_exe",
    #     parameters=[params_cam],
    # )

    record_node = Node(package="debug_cv", executable="record_vid")

    cv_node1 = Node(
        package="blobfish_cv",
        executable="detect",
        remappings=[
            ("~/flare_bbox", "/blobfish_cv/flare/pos"),
        ],
        name="detect_flare",
        parameters=[{"config_path": str(pkg_this / "config" / "detect_flare.yaml")}],
    )

    cv_node2 = Node(
        package="blobfish_cv",
        executable="detect",
        remappings=[
            ("~/gate_bbox", "/blobfish_cv/gate/pos"),
        ],
        name="detect_others",
        parameters=[{"config_path": str(pkg_this / "config" / "detect_others.yaml")}],
    )

    ld = LaunchDescription()
    # ld.add_action(cam_node)
    ld.add_action(record_node)
    ld.add_action(cv_node1)
    ld.add_action(cv_node2)
    return ld
