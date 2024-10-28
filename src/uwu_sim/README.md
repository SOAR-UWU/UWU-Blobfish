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

Listen to topic from CLI:

```sh
gz topic -e -t <topic_path>
```

If your GUI scale feels off:

```sh
# Add below to ~/.bashrc
export QT_SCALE_FACTOR=<insert scale>
export QT_AUTO_SCREEN_SCALE_FACTOR=0
```

## Modelling

Things to model: <https://sauvc.org/rulebook/#tasks>

- Exporting from Blender to Gazebo: <https://gazebosim.org/api/sim/8/tutorials.html#autotoc_md427>
- Moment of Inertia Calculator: <https://amesweb.info/inertia/mass-moment-of-inertia-calculator.aspx>
  - Recommended inside the beginner Gazebo tutorial series.
- ~~Between Fusion 360 & Gazebo, the axes are the exact same. Left and right on the orbit cube match Gazebo. Only difference is front and back are swapped.~~
  - ~~Its actually Fusion 360 that is confusing: <https://forums.autodesk.com/t5/fusion-design-validate-document/why-left-is-right-and-right-is-left/td-p/6623908>~~
- Gazebo uses positive X as forward, positive Y as left, and positive Z as up for hydrodynamics.
- Fusion to SDF exporter: <https://github.com/andreasBihlmaier/FusionSDF>
  - Out of 6 options, I tried this one first. Haven't tested the rest yet.
  - Correctly exports components as links and all joints.
  - Correctly exports materials.
  - Scaling is correct regardless of document units.
  - Have to correct the joint between base link and the main chassis.
  - Have to fix all collisions since it exports all components as box collisions.
  - Have to fix all joint types.
  - Haven't tested if inertial & mass estimation is correct, but should definitely adjust mass at least.

## Gazebo Customization

In both cases, specifying even a single plugin disables the defaults \*facepalm\*.

I swear are we overlapping RViz functionality here? But since RViz doesn't support SDF, maybe we can use the sim as the visualization tool too.

### Physics

- List of all physics plugins: <https://gazebosim.org/api/sim/8/namespacegz_1_1sim_1_1systems.html>

### UI

- List of all UI plugins: <https://gazebosim.org/api/gui/8/namespaceplugins.html>
  - Notable plugins below:
  - Display FPS: <https://gazebosim.org/api/gui/8/classplugins_1_1CameraFps.html>
  - Move to & follow object: <https://gazebosim.org/api/gui/8/classplugins_1_1CameraTracking.html>
  - Display image topic (i.e., camera feed): <https://gazebosim.org/api/gui/8/classplugins_1_1ImageDisplay.html>
  - Allow mouse to control camera: <https://gazebosim.org/api/gui/8/classplugins_1_1InteractiveViewControl.html>
  - Allow add & remove markers (i.e., waypoint tester): <https://gazebosim.org/api/gui/8/classplugins_1_1MarkerManager.html>
  - Receive all keyboard events: <https://gazebosim.org/api/gui/8/classgz_1_1gui_1_1KeyPublisher.html>
    - There is also an opinionated teleop plugin but its not suitable for our use case: <https://gazebosim.org/api/gui/8/classplugins_1_1Teleop.html>
  - Tape measure: <https://gazebosim.org/api/gui/8/classgz_1_1gui_1_1TapeMeasure.html>
  - Renderer: <https://gazebosim.org/api/gui/8/classplugins_1_1MinimalScene.html>
    - <https://gazebosim.org/api/sim/8/classgz_1_1sim_1_1GzSceneManager.html>
  - Sim start/stop: <https://gazebosim.org/api/gui/8/classplugins_1_1WorldControl.html>
  - Sim time stats: <https://gazebosim.org/api/gui/8/classplugins_1_1WorldStats.html>
  - Graph numeric topics: <https://gazebosim.org/api/gui/8/classplugins_1_1TransportPlotting.html>
  - View topic types (but not echo): <https://gazebosim.org/api/gui/8/classplugins_1_1TopicViewer.html>
  - Echo topic: <https://gazebosim.org/api/gui/8/classplugins_1_1TopicEcho.html>
    - tbh why isn't this part of view topic.
  - Entity tree: <https://gazebosim.org/api/sim/8/classgz_1_1sim_1_1EntityTree.html>
  - Apply force & torque by dragging (intuitive): <https://gazebosim.org/api/sim/8/classgz_1_1sim_1_1MouseDrag.html>
  - Apply arbitrary forces & torques (exact): <https://gazebosim.org/api/sim/8/classgz_1_1sim_1_1ApplyForceTorque.html>
  - View cube: <https://gazebosim.org/api/sim/8/classgz_1_1sim_1_1ViewAngle.html>
  - Transform tools: <https://gazebosim.org/api/sim/8/classgz_1_1sim_1_1TransformControl.html>
- Auto-generated default: `$HOME/.gz/sim/<#>/gui.config`
  - See: <https://gazebosim.org/api/sim/8/gui_config.html>
