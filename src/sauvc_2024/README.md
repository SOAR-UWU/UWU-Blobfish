Commands:

ros2 launch beluga_control base.launch.py
 - Launches all pid, cv, sensors files (not incl sensor hardware)

ros2 run beluga_hardware thruster_manager.py 
 - Runs thruster manager

ros2 run beluga_control sauvc_2024.py
 - Runs state machine for task control
