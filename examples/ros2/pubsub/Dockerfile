# Kubernetes image: runs both publisher and subscriber in one pod.
# For local testing with separate containers, use docker-compose.yaml instead.

FROM ros:humble-ros-base

WORKDIR /app
COPY publisher/publisher.py /app/publisher.py
COPY subscriber/subscriber.py /app/subscriber.py

CMD ["bash", "-c", "source /opt/ros/humble/setup.bash && python3 /app/publisher.py & python3 /app/subscriber.py & wait"]