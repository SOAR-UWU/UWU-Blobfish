import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import AnyLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    foxglove_pkg = get_package_share_directory("foxglove_bridge")

    foxglove_launch_dir = os.path.join(foxglove_pkg, "launch")
    foxglove_launch = IncludeLaunchDescription(
        AnyLaunchDescriptionSource(
            os.path.join(foxglove_launch_dir, "foxglove_bridge_launch.xml")
        )
    )

    # TODO: Move all the config files above & below into a single folder for ease of access?
    cam_node = Node(
        package="usb_cam",
        executable="usb_cam_node_exe",
        # TODO: Hardcoded here for now
        parameters=[
            dict(
                video_device="/dev/video0",
                framerate=60.0,
                image_width=640,
                image_height=480,
                brightness=100,
                contrast=100,
                saturation=100,
                sharpness=100,
                gain=-1,
                auto_white_balance=True,
                white_balance=4000,
                auto_exposure=True,
                exposure=-1,
                auto_focus=True,
                focus=-1,  # NOTE: the usb cam we use doesn't have software-controlled focus
            )
        ],
    )

    record_node = Node(package="debug_cv", executable="record_vid")

    cv_node = Node(package="blobfish_cv", executable="detect")

    # Create the launch description and populate
    # if hardware is not available, do not attempt to launch the IMU and Arduino nodes
    ld = LaunchDescription()
    ld.add_action(foxglove_launch)
    ld.add_action(cam_node)
    ld.add_action(record_node)
    ld.add_action(cv_node)
    return ld
