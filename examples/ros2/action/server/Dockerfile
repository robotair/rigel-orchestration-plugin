FROM ros:humble-ros-base

RUN apt-get update && apt-get install -y ros-humble-example-interfaces && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY server.py /app/

CMD ["bash", "-c", "source /opt/ros/humble/setup.bash && python3 /app/server.py"]
