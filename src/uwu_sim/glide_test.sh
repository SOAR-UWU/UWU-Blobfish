#!/usr/bin/env bash
source /opt/ros/humble/setup.bash

gz topic -t /blobfish/thruster/FL -m gz.msgs.Double -p 'data: 5.0'
gz topic -t /blobfish/thruster/FR -m gz.msgs.Double -p 'data: 5.0'

sleep 10

gz topic -t /blobfish/thruster/FL -m gz.msgs.Double -p 'data: 0.0'
gz topic -t /blobfish/thruster/FR -m gz.msgs.Double -p 'data: 0.0'
gz topic -t /blobfish/thruster/ML -m gz.msgs.Double -p 'data: 0.0'
gz topic -t /blobfish/thruster/MR -m gz.msgs.Double -p 'data: 0.0'
gz topic -t /blobfish/thruster/BL -m gz.msgs.Double -p 'data: 0.0'
gz topic -t /blobfish/thruster/BR -m gz.msgs.Double -p 'data: 0.0'
gz topic -t /blobfish/thruster/BM -m gz.msgs.Double -p 'data: 0.0'

sleep 10

gz topic -t /blobfish/thruster/BL -m gz.msgs.Double -p 'data: 5.0'
gz topic -t /blobfish/thruster/BR -m gz.msgs.Double -p 'data: 5.0'

sleep 10

gz topic -t /blobfish/thruster/FL -m gz.msgs.Double -p 'data: 0.0'
gz topic -t /blobfish/thruster/FR -m gz.msgs.Double -p 'data: 0.0'
gz topic -t /blobfish/thruster/ML -m gz.msgs.Double -p 'data: 0.0'
gz topic -t /blobfish/thruster/MR -m gz.msgs.Double -p 'data: 0.0'
gz topic -t /blobfish/thruster/BL -m gz.msgs.Double -p 'data: 0.0'
gz topic -t /blobfish/thruster/BR -m gz.msgs.Double -p 'data: 0.0'
gz topic -t /blobfish/thruster/BM -m gz.msgs.Double -p 'data: 0.0'
