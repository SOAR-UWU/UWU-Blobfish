#!/bin/env bash
dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)

if [[ -f "${dir}/.isaac_ros_common-config" ]]; then
    . "${dir}/.isaac_ros_common-config"
fi

. $dir/thirdparty/isaac_ros_common/scripts/run_dev.sh $dir
