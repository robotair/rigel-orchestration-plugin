#!/usr/bin/env python3
"""
ROS1 Service Client - Add Two Integers.

Continuously calls the 'add_two_ints' service with random numbers.
Used to demonstrate ROS1 Service communication between client/server nodes.
"""

import random

import rospy
from rospy_tutorials.srv import AddTwoInts


def call_add_two_ints(a, b):
    rospy.wait_for_service("add_two_ints")
    try:
        add_two_ints = rospy.ServiceProxy("add_two_ints", AddTwoInts)
        response = add_two_ints(a, b)
        return response.sum
    except rospy.ServiceException as e:
        rospy.logerr(f"Service call failed: {e}")
        return None


def client():
    rospy.init_node("add_two_ints_client")
    rospy.loginfo("Client started. Sending requests to 'add_two_ints'...")

    rate = rospy.Rate(1)  # 1 Hz
    while not rospy.is_shutdown():
        a = random.randint(0, 100)
        b = random.randint(0, 100)
        result = call_add_two_ints(a, b)
        if result is not None:
            rospy.loginfo(f"Result: {a} + {b} = {result}")
        rate.sleep()


if __name__ == "__main__":
    try:
        client()
    except rospy.ROSInterruptException:
        pass
