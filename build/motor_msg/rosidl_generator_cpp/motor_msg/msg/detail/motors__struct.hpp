// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from motor_msg:msg/Motors.idl
// generated code does not contain a copyright notice

#ifndef MOTOR_MSG__MSG__DETAIL__MOTORS__STRUCT_HPP_
#define MOTOR_MSG__MSG__DETAIL__MOTORS__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__motor_msg__msg__Motors __attribute__((deprecated))
#else
# define DEPRECATED__motor_msg__msg__Motors __declspec(deprecated)
#endif

namespace motor_msg
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct Motors_
{
  using Type = Motors_<ContainerAllocator>;

  explicit Motors_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->motor1 = 0;
      this->motor2 = 0;
      this->motor3 = 0;
      this->motor4 = 0;
      this->motor5 = 0;
      this->motor6 = 0;
      this->motor7 = 0;
    }
  }

  explicit Motors_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->motor1 = 0;
      this->motor2 = 0;
      this->motor3 = 0;
      this->motor4 = 0;
      this->motor5 = 0;
      this->motor6 = 0;
      this->motor7 = 0;
    }
  }

  // field types and members
  using _motor1_type =
    uint16_t;
  _motor1_type motor1;
  using _motor2_type =
    uint16_t;
  _motor2_type motor2;
  using _motor3_type =
    uint16_t;
  _motor3_type motor3;
  using _motor4_type =
    uint16_t;
  _motor4_type motor4;
  using _motor5_type =
    uint16_t;
  _motor5_type motor5;
  using _motor6_type =
    uint16_t;
  _motor6_type motor6;
  using _motor7_type =
    uint16_t;
  _motor7_type motor7;

  // setters for named parameter idiom
  Type & set__motor1(
    const uint16_t & _arg)
  {
    this->motor1 = _arg;
    return *this;
  }
  Type & set__motor2(
    const uint16_t & _arg)
  {
    this->motor2 = _arg;
    return *this;
  }
  Type & set__motor3(
    const uint16_t & _arg)
  {
    this->motor3 = _arg;
    return *this;
  }
  Type & set__motor4(
    const uint16_t & _arg)
  {
    this->motor4 = _arg;
    return *this;
  }
  Type & set__motor5(
    const uint16_t & _arg)
  {
    this->motor5 = _arg;
    return *this;
  }
  Type & set__motor6(
    const uint16_t & _arg)
  {
    this->motor6 = _arg;
    return *this;
  }
  Type & set__motor7(
    const uint16_t & _arg)
  {
    this->motor7 = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    motor_msg::msg::Motors_<ContainerAllocator> *;
  using ConstRawPtr =
    const motor_msg::msg::Motors_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<motor_msg::msg::Motors_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<motor_msg::msg::Motors_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      motor_msg::msg::Motors_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<motor_msg::msg::Motors_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      motor_msg::msg::Motors_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<motor_msg::msg::Motors_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<motor_msg::msg::Motors_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<motor_msg::msg::Motors_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__motor_msg__msg__Motors
    std::shared_ptr<motor_msg::msg::Motors_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__motor_msg__msg__Motors
    std::shared_ptr<motor_msg::msg::Motors_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Motors_ & other) const
  {
    if (this->motor1 != other.motor1) {
      return false;
    }
    if (this->motor2 != other.motor2) {
      return false;
    }
    if (this->motor3 != other.motor3) {
      return false;
    }
    if (this->motor4 != other.motor4) {
      return false;
    }
    if (this->motor5 != other.motor5) {
      return false;
    }
    if (this->motor6 != other.motor6) {
      return false;
    }
    if (this->motor7 != other.motor7) {
      return false;
    }
    return true;
  }
  bool operator!=(const Motors_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Motors_

// alias to use template instance with default allocator
using Motors =
  motor_msg::msg::Motors_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace motor_msg

#endif  // MOTOR_MSG__MSG__DETAIL__MOTORS__STRUCT_HPP_
