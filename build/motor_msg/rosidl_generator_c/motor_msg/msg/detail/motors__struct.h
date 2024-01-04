// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from motor_msg:msg/Motors.idl
// generated code does not contain a copyright notice

#ifndef MOTOR_MSG__MSG__DETAIL__MOTORS__STRUCT_H_
#define MOTOR_MSG__MSG__DETAIL__MOTORS__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in msg/Motors in the package motor_msg.
typedef struct motor_msg__msg__Motors
{
  uint16_t motor1;
  uint16_t motor2;
  uint16_t motor3;
  uint16_t motor4;
  uint16_t motor5;
  uint16_t motor6;
  uint16_t motor7;
} motor_msg__msg__Motors;

// Struct for a sequence of motor_msg__msg__Motors.
typedef struct motor_msg__msg__Motors__Sequence
{
  motor_msg__msg__Motors * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} motor_msg__msg__Motors__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // MOTOR_MSG__MSG__DETAIL__MOTORS__STRUCT_H_
