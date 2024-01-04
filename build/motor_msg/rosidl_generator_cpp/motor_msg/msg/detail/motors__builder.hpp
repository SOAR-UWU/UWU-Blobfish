// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from motor_msg:msg/Motors.idl
// generated code does not contain a copyright notice

#ifndef MOTOR_MSG__MSG__DETAIL__MOTORS__BUILDER_HPP_
#define MOTOR_MSG__MSG__DETAIL__MOTORS__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "motor_msg/msg/detail/motors__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace motor_msg
{

namespace msg
{

namespace builder
{

class Init_Motors_motor7
{
public:
  explicit Init_Motors_motor7(::motor_msg::msg::Motors & msg)
  : msg_(msg)
  {}
  ::motor_msg::msg::Motors motor7(::motor_msg::msg::Motors::_motor7_type arg)
  {
    msg_.motor7 = std::move(arg);
    return std::move(msg_);
  }

private:
  ::motor_msg::msg::Motors msg_;
};

class Init_Motors_motor6
{
public:
  explicit Init_Motors_motor6(::motor_msg::msg::Motors & msg)
  : msg_(msg)
  {}
  Init_Motors_motor7 motor6(::motor_msg::msg::Motors::_motor6_type arg)
  {
    msg_.motor6 = std::move(arg);
    return Init_Motors_motor7(msg_);
  }

private:
  ::motor_msg::msg::Motors msg_;
};

class Init_Motors_motor5
{
public:
  explicit Init_Motors_motor5(::motor_msg::msg::Motors & msg)
  : msg_(msg)
  {}
  Init_Motors_motor6 motor5(::motor_msg::msg::Motors::_motor5_type arg)
  {
    msg_.motor5 = std::move(arg);
    return Init_Motors_motor6(msg_);
  }

private:
  ::motor_msg::msg::Motors msg_;
};

class Init_Motors_motor4
{
public:
  explicit Init_Motors_motor4(::motor_msg::msg::Motors & msg)
  : msg_(msg)
  {}
  Init_Motors_motor5 motor4(::motor_msg::msg::Motors::_motor4_type arg)
  {
    msg_.motor4 = std::move(arg);
    return Init_Motors_motor5(msg_);
  }

private:
  ::motor_msg::msg::Motors msg_;
};

class Init_Motors_motor3
{
public:
  explicit Init_Motors_motor3(::motor_msg::msg::Motors & msg)
  : msg_(msg)
  {}
  Init_Motors_motor4 motor3(::motor_msg::msg::Motors::_motor3_type arg)
  {
    msg_.motor3 = std::move(arg);
    return Init_Motors_motor4(msg_);
  }

private:
  ::motor_msg::msg::Motors msg_;
};

class Init_Motors_motor2
{
public:
  explicit Init_Motors_motor2(::motor_msg::msg::Motors & msg)
  : msg_(msg)
  {}
  Init_Motors_motor3 motor2(::motor_msg::msg::Motors::_motor2_type arg)
  {
    msg_.motor2 = std::move(arg);
    return Init_Motors_motor3(msg_);
  }

private:
  ::motor_msg::msg::Motors msg_;
};

class Init_Motors_motor1
{
public:
  Init_Motors_motor1()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Motors_motor2 motor1(::motor_msg::msg::Motors::_motor1_type arg)
  {
    msg_.motor1 = std::move(arg);
    return Init_Motors_motor2(msg_);
  }

private:
  ::motor_msg::msg::Motors msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::motor_msg::msg::Motors>()
{
  return motor_msg::msg::builder::Init_Motors_motor1();
}

}  // namespace motor_msg

#endif  // MOTOR_MSG__MSG__DETAIL__MOTORS__BUILDER_HPP_
