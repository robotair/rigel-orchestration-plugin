FROM ros:humble-ros-base

WORKDIR /app
COPY publisher.py /app/

CMD ["bash", "-c", "source /opt/ros/humble/setup.bash && python3 /app/publisher.py"]
