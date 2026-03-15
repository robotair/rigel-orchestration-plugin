FROM ros:humble-ros-base

RUN apt-get update && apt-get install -y ros-humble-example-interfaces && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY client.py /app/

# Sleep briefly so the server is ready before the first goal is sent
CMD ["bash", "-c", "source /opt/ros/humble/setup.bash && sleep 5 && python3 /app/client.py"]
