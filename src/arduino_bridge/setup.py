from setuptools import find_packages, setup
import os
from glob import glob
from pathlib import Path

package_name = 'arduino_bridge'

def recursive_add_dir(folder):
    files = []
    share = Path("share") / package_name
    for dir in Path(folder).glob("**/"):
        files.append((str(share / dir), [str(p) for p in dir.glob("*.*")]))
    return files

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
        *recursive_add_dir('arduino'),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='javin',
    maintainer_email='javinenghp@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'bridge = arduino_bridge.arduino_listener:main'
        ],
    },
)
