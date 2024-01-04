# generated from ament/cmake/core/templates/nameConfig.cmake.in

# prevent multiple inclusion
if(_vectornav_CONFIG_INCLUDED)
  # ensure to keep the found flag the same
  if(NOT DEFINED vectornav_FOUND)
    # explicitly set it to FALSE, otherwise CMake will set it to TRUE
    set(vectornav_FOUND FALSE)
  elseif(NOT vectornav_FOUND)
    # use separate condition to avoid uninitialized variable warning
    set(vectornav_FOUND FALSE)
  endif()
  return()
endif()
set(_vectornav_CONFIG_INCLUDED TRUE)

# output package information
if(NOT vectornav_FIND_QUIETLY)
  message(STATUS "Found vectornav: 3.0.0 (${vectornav_DIR})")
endif()

# warn when using a deprecated package
if(NOT "" STREQUAL "")
  set(_msg "Package 'vectornav' is deprecated")
  # append custom deprecation text if available
  if(NOT "" STREQUAL "TRUE")
    set(_msg "${_msg} ()")
  endif()
  # optionally quiet the deprecation message
  if(NOT ${vectornav_DEPRECATED_QUIET})
    message(DEPRECATION "${_msg}")
  endif()
endif()

# flag package as ament-based to distinguish it after being find_package()-ed
set(vectornav_FOUND_AMENT_PACKAGE TRUE)

# include all config extra files
set(_extras "ament_cmake_export_dependencies-extras.cmake")
foreach(_extra ${_extras})
  include("${vectornav_DIR}/${_extra}")
endforeach()
