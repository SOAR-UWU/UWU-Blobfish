// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from motor_msg:msg/Motors.idl
// generated code does not contain a copyright notice

#ifndef MOTOR_MSG__MSG__DETAIL__MOTORS__TRAITS_HPP_
#define MOTOR_MSG__MSG__DETAIL__MOTORS__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "motor_msg/msg/detail/motors__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace motor_msg
{

namespace msg
{

inline void to_flow_style_yaml(
  const Motors & msg,
  std::ostream & out)
{
  out << "{";
  // member: motor1
  {
    out << "motor1: ";
    rosidl_generator_traits::value_to_yaml(msg.motor1, out);
    out << ", ";
  }

  // member: motor2
  {
    out << "motor2: ";
    rosidl_generator_traits::value_to_yaml(msg.motor2, out);
    out << ", ";
  }

  // member: motor3
  {
    out << "motor3: ";
    rosidl_generator_traits::value_to_yaml(msg.motor3, out);
    out << ", ";
  }

  // member: motor4
  {
    out << "motor4: ";
    rosidl_generator_traits::value_to_yaml(msg.motor4, out);
    out << ", ";
  }

  // member: motor5
  {
    out << "motor5: ";
    rosidl_generator_traits::value_to_yaml(msg.motor5, out);
    out << ", ";
  }

  // member: motor6
  {
    out << "motor6: ";
    rosidl_generator_traits::value_to_yaml(msg.motor6, out);
    out << ", ";
  }

  // member: motor7
  {
    out << "motor7: ";
    rosidl_generator_traits::value_to_yaml(msg.motor7, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const Motors & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: motor1
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "motor1: ";
    rosidl_generator_traits::value_to_yaml(msg.motor1, out);
    out << "\n";
  }

  // member: motor2
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "motor2: ";
    rosidl_generator_traits::value_to_yaml(msg.motor2, out);
    out << "\n";
  }

  // member: motor3
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "motor3: ";
    rosidl_generator_traits::value_to_yaml(msg.motor3, out);
    out << "\n";
  }

  // member: motor4
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "motor4: ";
    rosidl_generator_traits::value_to_yaml(msg.motor4, out);
    out << "\n";
  }

  // member: motor5
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "motor5: ";
    rosidl_generator_traits::value_to_yaml(msg.motor5, out);
    out << "\n";
  }

  // member: motor6
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "motor6: ";
    rosidl_generator_traits::value_to_yaml(msg.motor6, out);
    out << "\n";
  }

  // member: motor7
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "motor7: ";
    rosidl_generator_traits::value_to_yaml(msg.motor7, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Motors & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace motor_msg

namespace rosidl_generator_traits
{

[[deprecated("use motor_msg::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const motor_msg::msg::Motors & msg,
  std::ostream & out, size_t indentation = 0)
{
  motor_msg::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use motor_msg::msg::to_yaml() instead")]]
inline std::string to_yaml(const motor_msg::msg::Motors & msg)
{
  return motor_msg::msg::to_yaml(msg);
}

template<>
inline const char * data_type<motor_msg::msg::Motors>()
{
  return "motor_msg::msg::Motors";
}

template<>
inline const char * name<motor_msg::msg::Motors>()
{
  return "motor_msg/msg/Motors";
}

template<>
struct has_fixed_size<motor_msg::msg::Motors>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<motor_msg::msg::Motors>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<motor_msg::msg::Motors>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // MOTOR_MSG__MSG__DETAIL__MOTORS__TRAITS_HPP_
