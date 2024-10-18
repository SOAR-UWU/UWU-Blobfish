# UWU Sim

Package for UWU Simulator.

## Gazebo Documentation

We are using Gazebo Harmonic (v8.6.0), the latest version that supports ROS2 Humble.

### Tutorials

- Gazebo Beginner Tutorial Series: <https://gazebosim.org/docs/harmonic/tutorials>
  - Beginner-friendly tutorial series meant to get started with Gazebo.
- Gazebo Advanced Tutorial Index Page: <https://gazebosim.org/api/sim/8/tutorials.html>
  - Includes tutorials on every feature for advanced users. Of particular interest below:
  - **Maritime**: <https://gazebosim.org/api/sim/8/tutorials.html#autotoc_md428>
  - Migration from Gazebo classic: <https://gazebosim.org/api/sim/8/tutorials.html#autotoc_md421>
- Xacro Template Engine Guide: <https://github.com/ros/xacro/wiki>
  - Componentize URDF/SDF files.
- Gazebo Example ROS Package & Best Practices: <https://gazebosim.org/docs/harmonic/ros_gz_project_template_guide/>
  - Example launch files: <https://github.com/gazebosim/ros_gz/tree/ros2/ros_gz_sim_demos/launch>

### API References

- SDF Format v1.11 Documentation: <http://sdformat.org/spec?ver=1.11>
  - Harmonic supports up to v1.11. Tested by running `gz sim` with increasingly higher `<sdf version="1.XX">` till it complained.
- Gazebo API References Index Page: <https://gazebosim.org/docs/harmonic/library_reference_nav/>
  - Of particular interest below:
  - sim: <https://gazebosim.org/api/sim/8/index.html>
  - gui (writing frontend plugins): <https://gazebosim.org/api/gui/8/index.html>
  - The rest of the API references are incomplete since they were refactored out of the original monolithic documentation by Gazebo.

## Gazebo Commands

- Connecting ROS2 & Ignition topics: <https://gazebosim.org/docs/harmonic/ros2_integration>
- Bridge between Gazebo and ROS (include in uwu_sim/launch launch file):

```sh
ros2 run ros_gz_bridge parameter_bridge /TOPIC@ROS_MSG@GZ_MSG
```

After `colcon build` and `source install/setup.bash`, all `.sdf` worlds under `worlds/` will be visible to Gazebo, meaning you can directly `gz sim world_name.sdf` to load the world.

## Modelling

Things to model: <https://sauvc.org/rulebook/#tasks>

- Exporting from Blender to Gazebo: <https://gazebosim.org/api/sim/8/tutorials.html#autotoc_md427>
- Moment of Inertia Calculator: <https://amesweb.info/inertia/mass-moment-of-inertia-calculator.aspx>
  - Recommended inside the beginner Gazebo tutorial series.
