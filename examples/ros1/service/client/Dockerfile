FROM ros:noetic-ros-base

RUN apt-get update && apt-get install -y ros-noetic-rospy-tutorials && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY client.py /app/

# Sleep briefly so the server has time to start before the first call
CMD ["bash", "-c", "source /opt/ros/noetic/setup.bash && sleep 3 && python3 /app/client.py"]
