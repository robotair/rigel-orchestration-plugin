#!/usr/bin/env python3
"""
ROS2 Publisher Node - Number Sequence Publisher.

Publishes incrementing integers on /number_sequence topic at 1Hz.
Used to demonstrate Publisher/Subscriber communication between two ROS2 nodes.

Key differences from ROS1:
  - Uses rclpy instead of rospy
  - Node is a class inheriting from rclpy.node.Node
  - Timer-based publishing instead of Rate loop
  - No ROS Master needed (DDS peer-to-peer discovery)
"""

import socket

import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32


class NumberPublisher(Node):
    def __init__(self):
        super().__init__("number_publisher")
        self.publisher_ = self.create_publisher(Int32, "/number_sequence", 10)
        self.timer = self.create_timer(1.0, self.timer_callback)  # 1 Hz
        self.number = 0

        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        self.get_logger().info(f"Publisher started on {hostname} ({ip_address})")

    def timer_callback(self):
        self.number += 1
        msg = Int32()
        msg.data = self.number
        self.publisher_.publish(msg)
        self.get_logger().info(f"Publishing: {self.number}")


def main(args=None):
    rclpy.init(args=args)
    node = NumberPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
