// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from motor_msg:msg/Motors.idl
// generated code does not contain a copyright notice

#ifndef MOTOR_MSG__MSG__DETAIL__MOTORS__FUNCTIONS_H_
#define MOTOR_MSG__MSG__DETAIL__MOTORS__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/visibility_control.h"
#include "motor_msg/msg/rosidl_generator_c__visibility_control.h"

#include "motor_msg/msg/detail/motors__struct.h"

/// Initialize msg/Motors message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * motor_msg__msg__Motors
 * )) before or use
 * motor_msg__msg__Motors__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_motor_msg
bool
motor_msg__msg__Motors__init(motor_msg__msg__Motors * msg);

/// Finalize msg/Motors message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_motor_msg
void
motor_msg__msg__Motors__fini(motor_msg__msg__Motors * msg);

/// Create msg/Motors message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * motor_msg__msg__Motors__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_motor_msg
motor_msg__msg__Motors *
motor_msg__msg__Motors__create();

/// Destroy msg/Motors message.
/**
 * It calls
 * motor_msg__msg__Motors__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_motor_msg
void
motor_msg__msg__Motors__destroy(motor_msg__msg__Motors * msg);

/// Check for msg/Motors message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_motor_msg
bool
motor_msg__msg__Motors__are_equal(const motor_msg__msg__Motors * lhs, const motor_msg__msg__Motors * rhs);

/// Copy a msg/Motors message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_motor_msg
bool
motor_msg__msg__Motors__copy(
  const motor_msg__msg__Motors * input,
  motor_msg__msg__Motors * output);

/// Initialize array of msg/Motors messages.
/**
 * It allocates the memory for the number of elements and calls
 * motor_msg__msg__Motors__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_motor_msg
bool
motor_msg__msg__Motors__Sequence__init(motor_msg__msg__Motors__Sequence * array, size_t size);

/// Finalize array of msg/Motors messages.
/**
 * It calls
 * motor_msg__msg__Motors__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_motor_msg
void
motor_msg__msg__Motors__Sequence__fini(motor_msg__msg__Motors__Sequence * array);

/// Create array of msg/Motors messages.
/**
 * It allocates the memory for the array and calls
 * motor_msg__msg__Motors__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_motor_msg
motor_msg__msg__Motors__Sequence *
motor_msg__msg__Motors__Sequence__create(size_t size);

/// Destroy array of msg/Motors messages.
/**
 * It calls
 * motor_msg__msg__Motors__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_motor_msg
void
motor_msg__msg__Motors__Sequence__destroy(motor_msg__msg__Motors__Sequence * array);

/// Check for msg/Motors message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_motor_msg
bool
motor_msg__msg__Motors__Sequence__are_equal(const motor_msg__msg__Motors__Sequence * lhs, const motor_msg__msg__Motors__Sequence * rhs);

/// Copy an array of msg/Motors messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_motor_msg
bool
motor_msg__msg__Motors__Sequence__copy(
  const motor_msg__msg__Motors__Sequence * input,
  motor_msg__msg__Motors__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // MOTOR_MSG__MSG__DETAIL__MOTORS__FUNCTIONS_H_
