# Gazebo Commands

- Connecting ROS2 & Ignition topics: <https://gazebosim.org/docs/fortress/ros2_integration>
  - Bridge between Gazebo and ROS:

```sh
ros2 run ros_gz_bridge parameter_bridge /TOPIC@ROS_MSG@GZ_MSG

ros2 run ros_gz_bridge parameter_bridge /TOPIC@ROS_MSG@GZ_MSG
```

- ROS2 package for Gazebo best practices: <https://gazebosim.org/docs/fortress/ros_gz_project_template_guide>
  - Example launch files: <https://github.com/gazebosim/ros_gz/tree/ros2/ros_gz_sim_demos/launch>
- See all tutorials here: <https://gazebosim.org/docs/fortress/tutorials>
- Documentation for SDF format v1.9 <http://sdformat.org/spec?ver=1.9>
  - All supported properties for Gazebo Fortress which supports up to v1.9.
- Migrating Gazebo Classic to Ignition: <https://gazebosim.org/api/gazebo/6/migrationsdf.html>

## Modelling

Things to model: <https://sauvc.org/rulebook/#tasks>

- Exporting from Blender to Gazebo: <https://gazebosim.org/api/gazebo/6/blender_sdf_exporter.html>
  - Importing exported models to Fuel for easy access: <https://gazebosim.org/api/gazebo/6/meshtofuel.html>
- Underwater simulation plugins: <https://gazebosim.org/api/gazebo/6/underwater_vehicles.html>
- Xacro format guide: <https://github.com/ros/xacro/wiki>
  - Used to componentize creation of robot URDF
