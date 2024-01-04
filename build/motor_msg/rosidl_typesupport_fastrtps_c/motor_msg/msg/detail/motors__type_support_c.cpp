// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from motor_msg:msg/Motors.idl
// generated code does not contain a copyright notice
#include "motor_msg/msg/detail/motors__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "motor_msg/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "motor_msg/msg/detail/motors__struct.h"
#include "motor_msg/msg/detail/motors__functions.h"
#include "fastcdr/Cdr.h"

#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-parameter"
# ifdef __clang__
#  pragma clang diagnostic ignored "-Wdeprecated-register"
#  pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
# endif
#endif
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif

// includes and forward declarations of message dependencies and their conversion functions

#if defined(__cplusplus)
extern "C"
{
#endif


// forward declare type support functions


using _Motors__ros_msg_type = motor_msg__msg__Motors;

static bool _Motors__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const _Motors__ros_msg_type * ros_message = static_cast<const _Motors__ros_msg_type *>(untyped_ros_message);
  // Field name: motor1
  {
    cdr << ros_message->motor1;
  }

  // Field name: motor2
  {
    cdr << ros_message->motor2;
  }

  // Field name: motor3
  {
    cdr << ros_message->motor3;
  }

  // Field name: motor4
  {
    cdr << ros_message->motor4;
  }

  // Field name: motor5
  {
    cdr << ros_message->motor5;
  }

  // Field name: motor6
  {
    cdr << ros_message->motor6;
  }

  // Field name: motor7
  {
    cdr << ros_message->motor7;
  }

  return true;
}

static bool _Motors__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  _Motors__ros_msg_type * ros_message = static_cast<_Motors__ros_msg_type *>(untyped_ros_message);
  // Field name: motor1
  {
    cdr >> ros_message->motor1;
  }

  // Field name: motor2
  {
    cdr >> ros_message->motor2;
  }

  // Field name: motor3
  {
    cdr >> ros_message->motor3;
  }

  // Field name: motor4
  {
    cdr >> ros_message->motor4;
  }

  // Field name: motor5
  {
    cdr >> ros_message->motor5;
  }

  // Field name: motor6
  {
    cdr >> ros_message->motor6;
  }

  // Field name: motor7
  {
    cdr >> ros_message->motor7;
  }

  return true;
}  // NOLINT(readability/fn_size)

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_motor_msg
size_t get_serialized_size_motor_msg__msg__Motors(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _Motors__ros_msg_type * ros_message = static_cast<const _Motors__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // field.name motor1
  {
    size_t item_size = sizeof(ros_message->motor1);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name motor2
  {
    size_t item_size = sizeof(ros_message->motor2);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name motor3
  {
    size_t item_size = sizeof(ros_message->motor3);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name motor4
  {
    size_t item_size = sizeof(ros_message->motor4);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name motor5
  {
    size_t item_size = sizeof(ros_message->motor5);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name motor6
  {
    size_t item_size = sizeof(ros_message->motor6);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name motor7
  {
    size_t item_size = sizeof(ros_message->motor7);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

static uint32_t _Motors__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_motor_msg__msg__Motors(
      untyped_ros_message, 0));
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_motor_msg
size_t max_serialized_size_motor_msg__msg__Motors(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  size_t last_member_size = 0;
  (void)last_member_size;
  (void)padding;
  (void)wchar_size;

  full_bounded = true;
  is_plain = true;

  // member: motor1
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint16_t);
    current_alignment += array_size * sizeof(uint16_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint16_t));
  }
  // member: motor2
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint16_t);
    current_alignment += array_size * sizeof(uint16_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint16_t));
  }
  // member: motor3
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint16_t);
    current_alignment += array_size * sizeof(uint16_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint16_t));
  }
  // member: motor4
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint16_t);
    current_alignment += array_size * sizeof(uint16_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint16_t));
  }
  // member: motor5
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint16_t);
    current_alignment += array_size * sizeof(uint16_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint16_t));
  }
  // member: motor6
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint16_t);
    current_alignment += array_size * sizeof(uint16_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint16_t));
  }
  // member: motor7
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint16_t);
    current_alignment += array_size * sizeof(uint16_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint16_t));
  }

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = motor_msg__msg__Motors;
    is_plain =
      (
      offsetof(DataType, motor7) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static size_t _Motors__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_motor_msg__msg__Motors(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_Motors = {
  "motor_msg::msg",
  "Motors",
  _Motors__cdr_serialize,
  _Motors__cdr_deserialize,
  _Motors__get_serialized_size,
  _Motors__max_serialized_size
};

static rosidl_message_type_support_t _Motors__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_Motors,
  get_message_typesupport_handle_function,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, motor_msg, msg, Motors)() {
  return &_Motors__type_support;
}

#if defined(__cplusplus)
}
#endif
