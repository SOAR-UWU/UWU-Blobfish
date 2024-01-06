from setuptools import find_packages, setup

package_name = 'pid_package'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
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
            'offset_calibrator = pid_package.pid_offset_calibration:main',
            'pid_node = pid_package.pid_package:main'
            'motor_dir_control_node = pid_package.direction_control:main'
        ],
    },
)
