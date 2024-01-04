from setuptools import find_packages
from setuptools import setup

setup(
    name='motor_msg',
    version='0.0.0',
    packages=find_packages(
        include=('motor_msg', 'motor_msg.*')),
)
