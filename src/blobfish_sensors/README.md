# About the VN-100

The VN-100 _doesn't_ support sending position. Any reference you see in code for it is for its successors the VN-200 and VN-300.

If you read the VN-100 User Manual (go google a pirated version), it may initially give the impression that it can send position. But it can't. In section 4.2.1, it explicitly states group 6 isn't used on VN-100. Group 6 is the group that would contain position data. This is because VN-100 doesn't have a GPS receiver. You can also check section 4.4, which shows the position & velocity field aren't used on the VN-100.

Even if we got a VN-200 however, do note underwater, even in a shallow pool, is a GNSS-denied situation. VectorNav won't send position (and velocity) info if it can't get a GPS fix, as according to the user manual. Its better to just research stuff like `robot_localization` or pose EKF (Extended Kalman Filter), or generally how to localize in a GNSS-denied environment. Maybe optical flow, or aligning to walls using the depth camera? Who knows if SLAM is viable, the prof said (in 2024) it wasn't, but while the seniors may have tried, a genius hasn't tried yet.

## Entering Command Prompt Mode

Send the above over serial, ensuring the right baud rate is set and LF line endings are in use:

```txt
# Section 5.1.7: Entering Command Mode
$VNCMD*XX

# Get out of Command Mode
system reset
```

See sections 5.5, 6.4 and 8.4 for some text commands. As for other special commands, refer to everything in section 5.1.

## Figuring out the Parameters

Go see these two files:

- [`vectornav.cc`](../../thirdparty/vectornav/vectornav/src/vectornav.cc): Has some in-code documentation on the parameters & which section was referred to.
- [`types.h`](../../thirdparty/vectornav/vectornav/vnproglib-1.2.0.0/cpp/include/vn/types.h): Contains the enums for the various options.

### About Baud Rate

- It's rumoured a lower baudrate is more stable to interference.
- If its not working, try going to the highest baudrate, then go back down.
- 921600 is the highest, 115200 is the default... and the minimum tested to work if using CommonField=0x7FFF at 40Hz.
- Higher Hz needs higher baudrate.

## Common Group Option

`1111 1111 1111 1111`

Based on `types.h`, to turn on all fields of common group, use `0x7FFF`.

However, the VN-100 leaves some fields blank, so to save baud rate, use `0x2f3d` (`hex(0b0010111100111101)`) instead. See section 4.4 for info on what is enabled.

As for what we actually need, use `0x0138` (`hex(0b0000000100111000)`). Again, refer to section 4.4 to figure out why we turned specifically these on. `DeltaTheta` is disabled because although `dvel` actually seems to be linear velocity delta, its no more helpful than integrating acceleration directly.
