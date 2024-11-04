"""Launch file that compiles all .xacro files, removing the .xacro suffix.

Yes, it will throw errors for non-standalone xacro files, but those are harmless
to compile anyways.
"""

from ament_index_python.packages import get_package_share_path
from launch import LaunchDescription
from launch.actions import ExecuteProcess, LogInfo


def generate_launch_description():
    pkg_uwu_sim = get_package_share_path("uwu_sim")

    ld = LaunchDescription()
    for path in pkg_uwu_sim.rglob("*.xacro"):
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
