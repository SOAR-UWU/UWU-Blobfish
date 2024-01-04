// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from motor_msg:msg/Motors.idl
// generated code does not contain a copyright notice
#include "motor_msg/msg/detail/motors__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


bool
motor_msg__msg__Motors__init(motor_msg__msg__Motors * msg)
{
  if (!msg) {
    return false;
  }
  // motor1
  // motor2
  // motor3
  // motor4
  // motor5
  // motor6
  // motor7
  return true;
}

void
motor_msg__msg__Motors__fini(motor_msg__msg__Motors * msg)
{
  if (!msg) {
    return;
  }
  // motor1
  // motor2
  // motor3
  // motor4
  // motor5
  // motor6
  // motor7
}

bool
motor_msg__msg__Motors__are_equal(const motor_msg__msg__Motors * lhs, const motor_msg__msg__Motors * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // motor1
  if (lhs->motor1 != rhs->motor1) {
    return false;
  }
  // motor2
  if (lhs->motor2 != rhs->motor2) {
    return false;
  }
  // motor3
  if (lhs->motor3 != rhs->motor3) {
    return false;
  }
  // motor4
  if (lhs->motor4 != rhs->motor4) {
    return false;
  }
  // motor5
  if (lhs->motor5 != rhs->motor5) {
    return false;
  }
  // motor6
  if (lhs->motor6 != rhs->motor6) {
    return false;
  }
  // motor7
  if (lhs->motor7 != rhs->motor7) {
    return false;
  }
  return true;
}

bool
motor_msg__msg__Motors__copy(
  const motor_msg__msg__Motors * input,
  motor_msg__msg__Motors * output)
{
  if (!input || !output) {
    return false;
  }
  // motor1
  output->motor1 = input->motor1;
  // motor2
  output->motor2 = input->motor2;
  // motor3
  output->motor3 = input->motor3;
  // motor4
  output->motor4 = input->motor4;
  // motor5
  output->motor5 = input->motor5;
  // motor6
  output->motor6 = input->motor6;
  // motor7
  output->motor7 = input->motor7;
  return true;
}

motor_msg__msg__Motors *
motor_msg__msg__Motors__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  motor_msg__msg__Motors * msg = (motor_msg__msg__Motors *)allocator.allocate(sizeof(motor_msg__msg__Motors), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(motor_msg__msg__Motors));
  bool success = motor_msg__msg__Motors__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
motor_msg__msg__Motors__destroy(motor_msg__msg__Motors * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    motor_msg__msg__Motors__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
motor_msg__msg__Motors__Sequence__init(motor_msg__msg__Motors__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  motor_msg__msg__Motors * data = NULL;

  if (size) {
    data = (motor_msg__msg__Motors *)allocator.zero_allocate(size, sizeof(motor_msg__msg__Motors), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = motor_msg__msg__Motors__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        motor_msg__msg__Motors__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
motor_msg__msg__Motors__Sequence__fini(motor_msg__msg__Motors__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      motor_msg__msg__Motors__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

motor_msg__msg__Motors__Sequence *
motor_msg__msg__Motors__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  motor_msg__msg__Motors__Sequence * array = (motor_msg__msg__Motors__Sequence *)allocator.allocate(sizeof(motor_msg__msg__Motors__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = motor_msg__msg__Motors__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
motor_msg__msg__Motors__Sequence__destroy(motor_msg__msg__Motors__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    motor_msg__msg__Motors__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
motor_msg__msg__Motors__Sequence__are_equal(const motor_msg__msg__Motors__Sequence * lhs, const motor_msg__msg__Motors__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!motor_msg__msg__Motors__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
motor_msg__msg__Motors__Sequence__copy(
  const motor_msg__msg__Motors__Sequence * input,
  motor_msg__msg__Motors__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(motor_msg__msg__Motors);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    motor_msg__msg__Motors * data =
      (motor_msg__msg__Motors *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!motor_msg__msg__Motors__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          motor_msg__msg__Motors__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!motor_msg__msg__Motors__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
