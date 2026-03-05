FROM ros:humble-ros-base

WORKDIR /app
COPY subscriber.py /app/

CMD ["bash", "-c", "source /opt/ros/humble/setup.bash && python3 /app/subscriber.py"]
