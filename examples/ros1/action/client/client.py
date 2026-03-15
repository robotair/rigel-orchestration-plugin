#!/usr/bin/env python3
"""
ROS1 Action Client - Fibonacci Sequence.

Sends goals to the 'fibonacci' action server requesting Fibonacci sequences.
Prints feedback as the sequence is being computed.
Used to demonstrate ROS1 Action communication between client/server nodes.
"""

import random

import rospy
import actionlib

from my_package.msg import FibonacciAction, FibonacciGoal


def feedback_cb(feedback):
    rospy.loginfo(f"[Feedback] Partial sequence: {feedback.partial_sequence}")


def main():
    rospy.init_node("fibonacci_client")

    client = actionlib.SimpleActionClient("fibonacci", FibonacciAction)
    rospy.loginfo("Waiting for 'fibonacci' action server...")
    client.wait_for_server()
    rospy.loginfo("Connected to 'fibonacci' action server.")

    rate = rospy.Rate(0.1)  # One goal every 10 seconds
    while not rospy.is_shutdown():
        order = random.randint(5, 15)
        rospy.loginfo(f"Sending goal: Fibonacci({order})")

        goal = FibonacciGoal()
        goal.order = order
        client.send_goal(goal, feedback_cb=feedback_cb)
        client.wait_for_result()

        result = client.get_result()
        if result:
            rospy.loginfo(f"[Result] Sequence: {result.sequence}")

        rate.sleep()


if __name__ == "__main__":
    try:
        main()
    except rospy.ROSInterruptException:
        pass
