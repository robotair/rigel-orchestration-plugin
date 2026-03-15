# Build context must be the action/ root directory (not client/) so we can
# access Fibonacci.action, package.xml, and CMakeLists.txt.
# Use: docker compose up (docker-compose.yaml sets context: . and dockerfile: ./client/Dockerfile)

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
# Both server.py and client.py must exist for catkin_install_python to succeed
WORKDIR /ros_workspace
COPY Fibonacci.action /ros_workspace/src/my_package/Fibonacci.action
COPY package.xml /ros_workspace/src/my_package/package.xml
COPY CMakeLists.txt /ros_workspace/src/my_package/CMakeLists.txt
COPY server/server.py /ros_workspace/src/my_package/server/server.py
COPY client/client.py /ros_workspace/src/my_package/client/client.py

RUN /bin/bash -c "source /opt/ros/noetic/setup.bash && catkin_make"

# Copy client script (sleep so server is ready before first call)
COPY client/client.py /app/client.py
RUN chmod +x /app/client.py

CMD ["bash", "-c", "source /opt/ros/noetic/setup.bash && source /ros_workspace/devel/setup.bash && sleep 5 && python3 /app/client.py"]
