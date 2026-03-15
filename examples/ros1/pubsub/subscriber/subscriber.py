#!/usr/bin/env python3
"""
ROS1 Subscriber Node - Number Sequence Subscriber.

Subscribes to /number_sequence topic and logs received messages.
Used to demonstrate Publisher/Subscriber communication between two ROS1 nodes.
"""

import os
import socket

import rospy
from std_msgs.msg import Int32


class NumberSubscriber:
    def __init__(self):
        self.received_count = 0
        self.expected_number = 1
        hostname = socket.gethostname()
        ip_address = os.environ.get("ROS_IP") or socket.gethostbyname(hostname)
        rospy.loginfo(f"Subscriber started on {hostname} ({ip_address})")
        rospy.Subscriber("/number_sequence", Int32, self.callback)

    def callback(self, msg):
        self.received_count += 1
        rospy.loginfo(f"Received: {msg.data} (total: {self.received_count})")

        if msg.data != self.expected_number:
            missed = list(range(self.expected_number, msg.data))
            rospy.logwarn(f"Missed numbers: {missed}")

        self.expected_number = msg.data + 1

    def run(self):
        rospy.spin()
        rospy.loginfo(f"Shutting down. Total received: {self.received_count}")


if __name__ == "__main__":
    try:
        rospy.init_node("number_subscriber", anonymous=False)
        subscriber = NumberSubscriber()
        subscriber.run()
    except rospy.ROSInterruptException:
        pass
