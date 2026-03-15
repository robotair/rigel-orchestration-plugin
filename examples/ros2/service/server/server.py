#!/usr/bin/env python3
"""
ROS2 Service Server - Add Two Integers.

Provides the 'add_two_ints' service that sums two integers.
Used to demonstrate ROS2 Service communication between client/server nodes.

Key differences from ROS1:
  - Uses rclpy instead of rospy
  - Service type from example_interfaces (standard ROS2 package)
  - Node class-based architecture
  - No ROS Master needed
"""

import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts


class AddTwoIntsServer(Node):
    def __init__(self):
        super().__init__("add_two_ints_server")
        self.srv = self.create_service(
            AddTwoInts, "add_two_ints", self.handle_request
        )
        self.get_logger().info("Service 'add_two_ints' ready.")

    def handle_request(self, request, response):
        response.sum = request.a + request.b
        self.get_logger().info(f"Request: {request.a} + {request.b} = {response.sum}")
        return response


def main(args=None):
    rclpy.init(args=args)
    node = AddTwoIntsServer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
