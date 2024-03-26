from glob import glob

from setuptools import find_packages, setup

package_name = "blobfish_cv"

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
    maintainer="jh2xl",
    maintainer_email="42513874+Interpause@users.noreply.github.com",
    description="CV stuff",
    license="TODO: License declaration",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": ["detect = blobfish_cv.detect:main"],
    },
)
