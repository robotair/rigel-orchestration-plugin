cmake_minimum_required(VERSION 3.0.2)
project(my_package)

find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  actionlib
  actionlib_msgs
  message_generation
)

add_action_files(
  DIRECTORY .
  FILES Fibonacci.action
)

generate_messages(
  DEPENDENCIES actionlib_msgs std_msgs
)

catkin_package(
  CATKIN_DEPENDS rospy std_msgs actionlib actionlib_msgs message_runtime
)

catkin_install_python(PROGRAMS
  server/server.py
  client/client.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
