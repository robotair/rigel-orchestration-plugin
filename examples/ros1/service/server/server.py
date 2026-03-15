#!/usr/bin/env python3
"""
ROS1 Service Server - Add Two Integers.

Provides the 'add_two_ints' service that sums two integers.
Used to demonstrate ROS1 Service communication between client/server nodes.
"""

import rospy
from rospy_tutorials.srv import AddTwoInts, AddTwoIntsResponse


def handle_add_two_ints(req):
    result = req.a + req.b
    rospy.loginfo(f"Request: {req.a} + {req.b} = {result}")
    return AddTwoIntsResponse(result)


def server():
    rospy.init_node("add_two_ints_server")
    rospy.Service("add_two_ints", AddTwoInts, handle_add_two_ints)
    rospy.loginfo("Service 'add_two_ints' ready.")
    rospy.spin()


if __name__ == "__main__":
    server()
