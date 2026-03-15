#!/usr/bin/env python3
"""
ROS1 Publisher Node - Number Sequence Publisher.

Publishes incrementing integers on /number_sequence topic at 1Hz.
Used to demonstrate Publisher/Subscriber communication between two ROS1 nodes.
"""

import os
import socket

import rospy
from std_msgs.msg import Int32


def publisher():
    rospy.init_node("number_publisher", anonymous=False)
    pub = rospy.Publisher("/number_sequence", Int32, queue_size=10)
    rate = rospy.Rate(1)  # 1 Hz

    hostname = socket.gethostname()
    ip_address = os.environ.get("ROS_IP") or socket.gethostbyname(hostname)
    rospy.loginfo(f"Publisher started on {hostname} ({ip_address})")

    number = 0
    while not rospy.is_shutdown():
        number += 1
        rospy.loginfo(f"Publishing: {number}")
        pub.publish(number)
        rate.sleep()


if __name__ == "__main__":
    try:
        publisher()
    except rospy.ROSInterruptException:
        pass
