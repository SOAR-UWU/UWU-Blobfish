#!/bin/sh
dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
$dir/thirdparty/isaac_ros_common/scripts/run_dev.sh $dir
