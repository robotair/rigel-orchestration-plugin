#!/usr/bin/env python3
"""
ROS2 Action Client - Fibonacci Sequence.

Sends goals to the 'fibonacci' action server requesting Fibonacci sequences.
Prints feedback as the sequence is being computed.
Used to demonstrate ROS2 Action communication between client/server nodes.

Key differences from ROS1:
  - Uses rclpy.action.ActionClient instead of actionlib.SimpleActionClient
  - Async goal submission with futures
  - Feedback via callback registered on send_goal_async
  - No ROS Master needed
"""

import random
import time

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from example_interfaces.action import Fibonacci


class FibonacciClient(Node):
    def __init__(self):
        super().__init__("fibonacci_client")
        self._action_client = ActionClient(self, Fibonacci, "fibonacci")
        self.get_logger().info("Waiting for 'fibonacci' action server...")
        self._action_client.wait_for_server()
        self.get_logger().info("Connected to 'fibonacci' action server.")

    def send_goal(self, order):
        goal_msg = Fibonacci.Goal()
        goal_msg.order = order
        self.get_logger().info(f"Sending goal: Fibonacci({order})")

        send_goal_future = self._action_client.send_goal_async(
            goal_msg, feedback_callback=self.feedback_callback
        )
        send_goal_future.add_done_callback(self.goal_response_callback)

    def feedback_callback(self, feedback_msg):
        partial = list(feedback_msg.feedback.sequence)
        self.get_logger().info(f"[Feedback] Partial sequence: {partial}")

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warn("Goal rejected.")
            return

        self.get_logger().info("Goal accepted.")
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    def result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f"[Result] Sequence: {list(result.sequence)}")


def main(args=None):
    rclpy.init(args=args)
    node = FibonacciClient()

    try:
        while rclpy.ok():
            order = random.randint(5, 15)
            node.send_goal(order)
            # Spin to process callbacks
            rclpy.spin_once(node, timeout_sec=0.5)
            time.sleep(15.0)  # Wait between goals
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
