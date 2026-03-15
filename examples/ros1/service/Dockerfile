# Kubernetes image: runs both server and client in one pod.
# For local testing with separate containers, use docker-compose.yaml instead.

FROM ros:noetic-ros-base

RUN apt-get update && apt-get install -y ros-noetic-rospy-tutorials && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY server/server.py /app/server.py
COPY client/client.py /app/client.py

CMD ["bash", "-c", "source /opt/ros/noetic/setup.bash && python3 /app/server.py & sleep 3 && python3 /app/client.py & wait"]