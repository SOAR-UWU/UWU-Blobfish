#!/usr/bin/env bash
source /opt/ros/humble/setup.bash

gz topic -t /blobfish/FL -m gz.msgs.Double -p 'data: 0.0'
gz topic -t /blobfish/ML -m gz.msgs.Double -p 'data: 0.0'
gz topic -t /blobfish/BL -m gz.msgs.Double -p 'data: 0.0'
gz topic -t /blobfish/FR -m gz.msgs.Double -p 'data: 0.0'
gz topic -t /blobfish/MR -m gz.msgs.Double -p 'data: 0.0'
gz topic -t /blobfish/BR -m gz.msgs.Double -p 'data: 0.0'
gz topic -t /blobfish/BT -m gz.msgs.Double -p 'data: 0.0'
