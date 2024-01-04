#!/bin/sh
dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
$dir/uwu_main/isaac_ros_common/scripts/run_dev.sh $dir
