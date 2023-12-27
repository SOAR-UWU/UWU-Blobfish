#!/bin/bash

# USAGE: run ./push2robot.sh to compress all contents in the ~/workspaces/isaac_ros-dev folder and write it to the Jetson.
# An additional file name argument can be specified, in which case only files / folders in the isaac_ros-dev folder with names matching
# the file name will be pushed.

# EXAMPLE:
# ./push2robot.sh docker
# The folder and file named "docker", if they exist, are pushed to the bot as ~/pushed.

BOT_IP="SOAR-UWU@10.42.0.1"
cd ~/workspaces/isaac_ros-dev;
if [[-n $1]]    # if a CLI argument has been supplied
then
    echo $1 | xargs tar -cf - | ssh ${BOT_IP} -T "cat > ~/pushed";
else
    tar -cf - . | ssh ${BOT_IP} -T "cat > ~/pushed";
fi