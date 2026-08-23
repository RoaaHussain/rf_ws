cmake_minimum_required(VERSION 3.5)
project(my_bot)

# Default to C99
if(NOT CMAKE_C_STANDARD)
  set(CMAKE_C_STANDARD 99)
endif()

# Default to C++14
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # Skip copyright and cpplint if needed
  # set(ament_cmake_copyright_FOUND TRUE)
  # set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

# Install all directories
install(
  DIRECTORY config description launch worlds
  DESTINATION share/${PROJECT_NAME}
)

# No need for the second worlds install (the one above already covers it)
# install(DIRECTORY worlds/ DESTINATION share/${PROJECT_NAME}/worlds)

find_package(hardware_interface REQUIRED)
find_package(pluginlib REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_lifecycle REQUIRED)

add_library(my_bot_hardware SHARED src/my_bot_hardware.cpp)
target_compile_features(my_bot_hardware PUBLIC cxx_std_17)
target_include_directories(my_bot_hardware PUBLIC
  $<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include/my_bot>
)
ament_target_dependencies(my_bot_hardware PUBLIC
  hardware_interface pluginlib rclcpp rclcpp_lifecycle
)
target_link_libraries(my_bot_hardware PUBLIC serial)

pluginlib_export_plugin_description_file(hardware_interface my_bot_hardware.xml)

install(DIRECTORY include/ DESTINATION include/my_bot)
install(TARGETS my_bot_hardware
  EXPORT export_my_bot_hardware
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)
ament_export_targets(export_my_bot_hardware HAS_LIBRARY_TARGET)
ament_export_dependencies(hardware_interface pluginlib rclcpp rclcpp_lifecycle)
ament_package()