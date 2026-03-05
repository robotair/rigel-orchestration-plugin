# Kubernetes image: runs both publisher and subscriber in one pod.
# For local testing with separate containers, use docker-compose.yaml instead.

FROM ros:noetic-ros-base

RUN apt-get update && apt-get install -y ros-noetic-std-msgs && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY publisher/publisher.py /app/publisher.py
COPY subscriber/subscriber.py /app/subscriber.py

CMD ["bash", "-c", "source /opt/ros/noetic/setup.bash && (python3 /app/publisher.py & python3 /app/subscriber.py & wait)"]
