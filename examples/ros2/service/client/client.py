#!/usr/bin/env python3
"""
ROS2 Service Client - Add Two Integers.

Continuously calls the 'add_two_ints' service with random numbers.
Used to demonstrate ROS2 Service communication between client/server nodes.

Key differences from ROS1:
  - Uses rclpy instead of rospy
  - Async service calls with futures
  - Service type from example_interfaces
  - No ROS Master needed
"""

import random
import time

import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts


class AddTwoIntsClient(Node):
    def __init__(self):
        super().__init__("add_two_ints_client")
        self.client = self.create_client(AddTwoInts, "add_two_ints")
        self.get_logger().info("Waiting for 'add_two_ints' service...")
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Service not available, waiting...")
        self.get_logger().info("Connected to 'add_two_ints' service.")

    def send_request(self, a, b):
        request = AddTwoInts.Request()
        request.a = a
        request.b = b
        future = self.client.call_async(request)
        return future


def main(args=None):
    rclpy.init(args=args)
    node = AddTwoIntsClient()

    try:
        while rclpy.ok():
            a = random.randint(0, 100)
            b = random.randint(0, 100)

            future = node.send_request(a, b)
            rclpy.spin_until_future_complete(node, future)

            result = future.result()
            if result is not None:
                node.get_logger().info(f"Result: {a} + {b} = {result.sum}")

            time.sleep(1.0)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
