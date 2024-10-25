#!/usr/bin/env bash
source /opt/ros/humble/setup.bash

gz topic -t /blobfish/FL -m gz.msgs.Double -p 'data: 5.0'
gz topic -t /blobfish/FR -m gz.msgs.Double -p 'data: 5.0'

sleep 10

gz topic -t /blobfish/FL -m gz.msgs.Double -p 'data: 0.0'
gz topic -t /blobfish/FR -m gz.msgs.Double -p 'data: 0.0'

sleep 10

gz topic -t /blobfish/BL -m gz.msgs.Double -p 'data: 5.0'
gz topic -t /blobfish/BR -m gz.msgs.Double -p 'data: 5.0'

sleep 10

gz topic -t /blobfish/BL -m gz.msgs.Double -p 'data: 0.0'
gz topic -t /blobfish/BR -m gz.msgs.Double -p 'data: 0.0'
