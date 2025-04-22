# Copyright 2016 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# What topic to publish motion commands to?
# /turtle1/pose
# What topic to publish rotation to?
# /turtle1/pose
# What topic to publish Linear Velocity to?
# /turtle1/cmd_vel
# (Listener) Subscribe to something that tells you where the turtle is
# Design a controller to get close to that position

import rclpy
import math
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

# diff_drive/lidar_link // Unknown, cant be accessed

# diff_drive/scan // range from hitting a wall [sensor_msgs/msgs/LaserScan]
# diff_drive/cmd_vel // Linear and angular data [geometry_msgs/smg/Twist]

# Using an always go left technique
# Use radians: pi/2, pi, 3pi/2, 2pi

class MinimalPublisher(Node):
    def __init__(self):
        super().__init__('minimal_publisher')

        # Publusher / Subscribers
        self.velocity_publisher = self.create_publisher(Twist, '/diff_drive/cmd_vel', 10)
        self.laser_scanner = self.create_subscription(LaserScan, 'diff_drive/scan', self.laser_callback, 10)
        # self.cmd_vel_timer = self.create_timer(0.1, self.publish_cmd_vel) # Timer based?

        # Paramaters
        self.wall_threshhold = 3.0
        self.linear_speed = 0.2
        self.angular_speed = 1.0
        self.curr_cmd = Twist()

        # State Machine
        self.isRotating = False
        self.state = 'initial_rotation'

        # Goals (Rotational)
        self.goal_x = 0
        self.goal_y = 0



    def laser_callback(self, msg):
        wall_distance = msg.ranges[0]

        if self.state == "moving_foward":
            if wall_distance >= self.wall_threshhold:
                self.state = "rotating"
                self.curr_cmd.linear.x = 0
                self.curr_cmd.angular.z = -self.angular_speed
            else:
                self.curr_cmd.linear.x = self.linear_speed
                self.curr_cmd.angular.z = 0
        elif self.state == "rotating":
            if wall_distance >= self.wall_threshhold:
                self.state = "moving_foward"
                self.curr_cmd.linear.x = self.linear_speed
                self.curr_cmd.angular.z = 0
                
        self.velocity_publisher.publish(self.curr_cmd)


def main(args=None):
    rclpy.init(args=args)
    minimal_publisher = MinimalPublisher()
    rclpy.spin(minimal_publisher)
    minimal_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
