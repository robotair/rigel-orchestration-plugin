FROM ros:noetic-ros-base

RUN apt-get update && apt-get install -y ros-noetic-rospy-tutorials && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY server.py /app/

CMD ["bash", "-c", "source /opt/ros/noetic/setup.bash && python3 /app/server.py"]
