import os
import sys
from glob import glob
from setuptools import find_packages, setup

package_name = 'blobfish_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='javin',
    maintainer_email='javin@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            "key_publisher = blobfish_control.publish_key:main",
            "manual_setpoint = blobfish_control.manual_setpoints:main",
            "base_strategy = blobfish_control.base_strategy:main",
            "sauvc_2024 = blobfish_control.sauvc_2024:main",
        ],
    },
)
