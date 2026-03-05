#!/usr/bin/env python3
"""
ROS2 Action Server - Fibonacci Sequence.

Computes Fibonacci sequences via the 'fibonacci' action.
Sends incremental feedback as each number is computed.
Used to demonstrate ROS2 Action communication between client/server nodes.

Key differences from ROS1:
  - Uses rclpy.action instead of actionlib
  - Action type from example_interfaces (standard ROS2 package)
  - Server created with ActionServer class
  - Async execution callback
  - No ROS Master needed
"""

import time

import rclpy
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.node import Node
from example_interfaces.action import Fibonacci


class FibonacciServer(Node):
    def __init__(self):
        super().__init__("fibonacci_server")
        self._action_server = ActionServer(
            self,
            Fibonacci,
            "fibonacci",
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
        )
        self.get_logger().info("Fibonacci action server started.")

    def goal_callback(self, goal_request):
        self.get_logger().info(
            f"Received goal: compute Fibonacci({goal_request.order})"
        )
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        self.get_logger().warn("Received cancel request.")
        return CancelResponse.ACCEPT

    async def execute_callback(self, goal_handle):
        self.get_logger().info("Executing goal...")
        feedback_msg = Fibonacci.Feedback()
        feedback_msg.sequence = [0, 1]

        for i in range(1, goal_handle.request.order):
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().warn("Goal canceled.")
                return Fibonacci.Result()

            next_num = feedback_msg.sequence[-1] + feedback_msg.sequence[-2]
            feedback_msg.sequence.append(next_num)
            self.get_logger().info(f"Feedback: {list(feedback_msg.sequence)}")
            goal_handle.publish_feedback(feedback_msg)

            # Simulate computation time
            time.sleep(1.0)

        goal_handle.succeed()
        result = Fibonacci.Result()
        result.sequence = feedback_msg.sequence
        self.get_logger().info(f"Goal succeeded: {list(result.sequence)}")
        return result


def main(args=None):
    rclpy.init(args=args)
    node = FibonacciServer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
