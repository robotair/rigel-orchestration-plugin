# Kubernetes image: runs both action server and client in one pod.
# Requires catkin_make to build the custom Fibonacci message type.
# For local testing with separate containers, use docker-compose.yaml instead.

FROM ros:noetic-ros-core

RUN apt-get update && apt-get install -y \
    python3 \
    build-essential \
    ros-noetic-rospy \
    ros-noetic-actionlib \
    ros-noetic-actionlib-msgs \
    ros-noetic-std-msgs \
    && rm -rf /var/lib/apt/lists/*

# Build catkin workspace to generate Fibonacci message classes
WORKDIR /ros_workspace
COPY Fibonacci.action /ros_workspace/src/my_package/Fibonacci.action
COPY package.xml /ros_workspace/src/my_package/package.xml
COPY CMakeLists.txt /ros_workspace/src/my_package/CMakeLists.txt
COPY server/server.py /ros_workspace/src/my_package/server/server.py
COPY client/client.py /ros_workspace/src/my_package/client/client.py

RUN /bin/bash -c "source /opt/ros/noetic/setup.bash && catkin_make && catkin_make install"

CMD ["bash", "-c", "source /opt/ros/noetic/setup.bash && source /ros_workspace/devel/setup.bash && rosrun my_package server.py & sleep 5 && rosrun my_package client.py & wait"]