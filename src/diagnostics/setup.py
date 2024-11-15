from glob import glob

from setuptools import find_packages, setup

package_name = "diagnostics"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (f"share/{package_name}/launch", glob("launch/*")),
        (f"share/{package_name}/config", glob("config/*")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="J-H",
    maintainer_email="42513874+Interpause@users.noreply.github.com",
    description="Package description",
    license="License declaration",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "motor = diagnostics.motor:main",
            "monitor = diagnostics.monitor:main",
        ],
    },
)
