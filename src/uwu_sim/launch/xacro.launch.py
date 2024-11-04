"""Launch file that compiles all .xacro files, removing the .xacro suffix.

Yes, it will throw errors for non-standalone xacro files, but those are harmless
to compile anyways.
"""

from ament_index_python.packages import get_package_share_path
from launch import LaunchDescription
from launch.actions import ExecuteProcess, LogInfo

IGNORE = [
    "robots/beluga",
]


def build_ignore_set():
    pkg_uwu_sim = get_package_share_path("uwu_sim")
    ignore_set = set()
    for entry in IGNORE:
        path = pkg_uwu_sim / entry
        if path.is_file():
            ignore_set.add(path)
            continue

        for xacro in (pkg_uwu_sim / entry).rglob("*.xacro"):
            ignore_set.add(xacro)
    return ignore_set


def generate_launch_description():
    pkg_uwu_sim = get_package_share_path("uwu_sim")
    ignore = build_ignore_set()

    ld = LaunchDescription()
    for path in pkg_uwu_sim.rglob("*.xacro"):
        if path in ignore:
            continue

        out_path = path.with_suffix("")
        log1 = LogInfo(msg=f"Found xacro: {path}")
        compile = ExecuteProcess(
            name=f"xacro({path.name})",
            # || true silences error codes
            cmd=["xacro", str(path), ">", str(out_path)],
            output={},
            shell=True,
        )
        log2 = LogInfo(msg=f"Compiled xacro: {out_path}")

        # ld.add_action(log1)
        ld.add_action(compile)
        # ld.add_action(log2)

    return ld
