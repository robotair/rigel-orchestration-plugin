#!/usr/bin/env python3
"""
ROS2 Subscriber Node - Number Sequence Subscriber.

Subscribes to /number_sequence topic and logs received messages.
Used to demonstrate Publisher/Subscriber communication between two ROS2 nodes.

Key differences from ROS1:
  - Uses rclpy instead of rospy
  - Subscription callback registered in constructor
  - No ROS Master needed (DDS peer-to-peer discovery)
"""

import socket

import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32


class NumberSubscriber(Node):
    def __init__(self):
        super().__init__("number_subscriber")
        self.subscription = self.create_subscription(
            Int32, "/number_sequence", self.callback, 10
        )
        self.received_count = 0
        self.expected_number = 1

        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        self.get_logger().info(f"Subscriber started on {hostname} ({ip_address})")

    def callback(self, msg):
        self.received_count += 1
        self.get_logger().info(
            f"Received: {msg.data} (total: {self.received_count})"
        )

        if msg.data != self.expected_number:
            missed = list(range(self.expected_number, msg.data))
            self.get_logger().warn(f"Missed numbers: {missed}")

        self.expected_number = msg.data + 1


def main(args=None):
    rclpy.init(args=args)
    node = NumberSubscriber()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.get_logger().info(f"Shutting down. Total received: {node.received_count}")
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
