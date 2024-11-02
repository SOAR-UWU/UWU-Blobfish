from glob import glob

from setuptools import find_packages, setup

package_name = "blobfish_sim"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (f"share/{package_name}/launch", glob("launch/*")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Interpause",
    maintainer_email="42513874+Interpause@users.noreply.github.com",
    description="ROS2 Gazebo Bridge Nodes",
    license="TODO: License declaration",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "sim_keypress = blobfish_sim.keypress:main",
            "sim_imu = blobfish_sim.imu:main",
            "sim_arduino = blobfish_sim.arduino:main",
        ],
    },
)
