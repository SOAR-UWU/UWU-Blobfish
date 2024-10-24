# Blobsimp

Simulation simplified version of blobfish.

Launch file will automatically run the below command to generate the SDF:

```sh
xacro model.sdf.xacro > model.sdf
```

For testing:

```sh
gz topic -t /blobfish/FL -m gz.msgs.Double -p 'data: 30.0'
gz topic -t /blobfish/ML -m gz.msgs.Double -p 'data: 30.0'
gz topic -t /blobfish/BL -m gz.msgs.Double -p 'data: 30.0'
gz topic -t /blobfish/FR -m gz.msgs.Double -p 'data: 30.0'
gz topic -t /blobfish/MR -m gz.msgs.Double -p 'data: 30.0'
gz topic -t /blobfish/BR -m gz.msgs.Double -p 'data: 30.0'
gz topic -t /blobfish/BT -m gz.msgs.Double -p 'data: 30.0'
```

```sh
gz topic -t /blobfish/FL -m gz.msgs.Double -p 'data: 1.0'
gz topic -t /blobfish/FR -m gz.msgs.Double -p 'data: 0.5'
gz topic -t /blobfish/ML -m gz.msgs.Double -p 'data: 100.0'
gz topic -t /blobfish/MR -m gz.msgs.Double -p 'data: 100.0'
gz topic -t /blobfish/BR -m gz.msgs.Double -p 'data: 40.0'
```
