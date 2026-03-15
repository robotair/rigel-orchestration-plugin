FROM ros:noetic-ros-base

RUN apt-get update && apt-get install -y ros-noetic-std-msgs && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY publisher.py /app/

CMD ["bash", "-c", "source /opt/ros/noetic/setup.bash && python3 /app/publisher.py"]
