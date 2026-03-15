# Kubernetes image: runs both server and client in one pod.
# For local testing with separate containers, use docker-compose.yaml instead.

FROM ros:humble-ros-base

RUN apt-get update && apt-get install -y ros-humble-example-interfaces && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY server/server.py /app/server.py
COPY client/client.py /app/client.py

CMD ["bash", "-c", "source /opt/ros/humble/setup.bash && python3 /app/server.py & python3 /app/client.py & wait"]