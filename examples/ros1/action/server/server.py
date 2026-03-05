#!/usr/bin/env python3
"""
ROS1 Action Server - Fibonacci Sequence.

Computes Fibonacci sequences via the 'fibonacci' action.
Sends incremental feedback as each number is computed.
Used to demonstrate ROS1 Action communication between client/server nodes.
"""

import rospy
import actionlib

from my_package.msg import (
    FibonacciAction,
    FibonacciFeedback,
    FibonacciResult,
)


class FibonacciServer:
    def __init__(self):
        self._as = actionlib.SimpleActionServer(
            "fibonacci",
            FibonacciAction,
            execute_cb=self.execute_cb,
            auto_start=False,
        )
        self._as.start()
        rospy.loginfo("Fibonacci action server started.")

    def execute_cb(self, goal):
        rospy.loginfo(f"Received goal: compute Fibonacci({goal.order})")

        feedback = FibonacciFeedback()
        feedback.partial_sequence = [0, 1]

        for i in range(1, goal.order):
            if self._as.is_preempt_requested():
                rospy.logwarn("Goal preempted.")
                self._as.set_preempted()
                return

            next_num = feedback.partial_sequence[-1] + feedback.partial_sequence[-2]
            feedback.partial_sequence.append(next_num)
            rospy.loginfo(f"Feedback: {feedback.partial_sequence}")
            self._as.publish_feedback(feedback)

            # Simulate computation time
            rospy.sleep(1.0)

        result = FibonacciResult()
        result.sequence = feedback.partial_sequence
        rospy.loginfo(f"Goal succeeded: {result.sequence}")
        self._as.set_succeeded(result)


def main():
    rospy.init_node("fibonacci_server")
    FibonacciServer()
    rospy.spin()


if __name__ == "__main__":
    main()
