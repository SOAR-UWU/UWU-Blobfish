# TODO

Start small, prioritize & scale up. Forget the old code tech debt unless it happens to be useful.

## Steps

### Basic Model

Cuboid + 7 Thruster Cubes
  - Slight positive bouyancy
  - Thrusters are functional

### Teleop

Gazebo Teleop -> ROS Teleop Bridge -> Motion Stack -> Simulated Arduino Bridge -> Gazebo Thrusters

### Basic Sensors

Accelerometer, Gyroscope, Compass & Barometer -> ROS Bridge

  - btw the VN-100 has all 4, datasheet doesn't say resolution but range is similar to BlueRobotics Bar02 so might be less complex to use
  - ROS Bridge centralizes topic mapping from Gazebo to ROS; allows Gazebo to have its own hardcoded topic topography different from Blobfish & make it easy to remap since all in one node

### Easy Config

Key sim params easily adjustable from single config file with hot reload

  - i.e., bouyancy, inertia, thruster directions, thrust range

### Physical Accuracy

Find reasonable mass, size, moment of inertia & drag values

  - Add to Easy Config but ofc back up the most accurate values

### 3D Environment

Pool with size-accurate tile textures, size-accurate task models

### Visual Sensors

Front-facing 3D cam cube & bottom-facing 2D can cube

  - Allows sanity check of CV & optical flow code

### Adversarial Sensors

Add (skewed) Gaussian noise to all basic sensors

  - No need for CV since cant test rigorously anyways when not visually accurate

### Adversarial Environment

Add random environmental forces (i.e., waves) and others

  - Unreliable thrust

### Test Suite

Test control code across range of sim parameters

  - Can code still cope with slight changes?
  - i.e., different slightly off thruster directions & max/min thrust, different bouyancy & inertia

### Prettify Sim

Accurate robot model

  - Not impt since robot can see the environment but not itself
