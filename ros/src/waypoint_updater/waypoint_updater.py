#!/usr/bin/env python

import numpy as np
import rospy
from geometry_msgs.msg import PoseStamped
from styx_msgs.msg import Lane, Waypoint
from scipy.spatial import KDTree
from std_msgs.msg import Int32

import math

'''
This node will publish waypoints from the car's current position to some `x` distance ahead.
As mentioned in the doc, you should ideally first implement a version which does not care
about traffic lights or obstacles.
Once you have created dbw_node, you will update this node to use the status of traffic lights too.
Please note that our simulator also provides the exact location of traffic lights and their
current status in `/vehicle/traffic_lights` message. You can use this message to build this node
as well as to verify your TL classifier.
'''

LOOKAHEAD_WPS = 10  # Number of waypoints we will publish. You can change this number
MAX_DECEL = .5
MAX_VEH_SPEED = 5.4 # Meter Per Second

class WaypointUpdater(object):
    def __init__(self):
        rospy.init_node('waypoint_updater')

        rospy.Subscriber('/current_pose', PoseStamped, self.pose_cb)
        rospy.Subscriber('/base_waypoints', Lane, self.waypoints_cb)
        rospy.Subscriber('/traffic_waypoint', Int32, self.traffic_cb)

        # TODO: Add a subscriber for /obstacle_waypoint below

        self.final_waypoints_pub = rospy.Publisher('final_waypoints', Lane, queue_size=1)

        self.pose = None
        self.stopline_wp_idx = -1
        self.base_waypoints = None
        self.waypoints_2d = None
        self.waypoint_tree = None
        self.stop_traffic_signal = False
        self.loop()


    def loop(self):
        rate = rospy.Rate(50)  # can go as low as 30Hz
        while not rospy.is_shutdown():
            if self.pose and self.base_waypoints:
                # Get closest waypoint
                closest_waypoint_idx = self.get_closest_waypoint_idx()
                self.publish_waypoints(closest_waypoint_idx)
            rate.sleep()

    def get_closest_waypoint_idx(self):
        x = self.pose.pose.position.x
        y = self.pose.pose.position.y
        closest_idx = self.waypoint_tree.query([x, y], 1)[1]

        # check if closest is ahead or behind vehilcle
        closest_coord = self.waypoints_2d[closest_idx]
        prev_coord = self.waypoints_2d[closest_idx - 1]

        # equation for hyperplane through closest_coords
        cl_vect = np.array(closest_coord)
        prev_vect = np.array(prev_coord)
        pos_vect = np.array([x, y])

        val = np.dot(cl_vect - prev_vect, pos_vect - cl_vect)

        if val > 0:
            closest_idx = (closest_idx + 1) % len(self.waypoints_2d)
        return closest_idx

    def publish_waypoints(self,closest_idx):
        lane = Lane()
        base_waypoints = self.base_waypoints.waypoints[closest_idx:(closest_idx+LOOKAHEAD_WPS)]
        #rospy.loginfo("stop waypoint idx %s\n", self.stopline_wp_idx)
        if self.stopline_wp_idx == -1 or (self.stopline_wp_idx >= (closest_idx+LOOKAHEAD_WPS)):
            updated_waypoints = []

            if(self.stop_traffic_signal == True):
                delta = MAX_VEH_SPEED/LOOKAHEAD_WPS
                for i, wp in enumerate(base_waypoints):
                    p = Waypoint()
                    p.pose = wp.pose
                    p.twist.twist.linear.x = min(MAX_VEH_SPEED, i*delta+2)
                    # rospy.loginfo("Decelerated Original: %s After: %s", wp.twist.twist.linear.x, p.twist.twist.linear.x)
                    updated_waypoints.append(p)
                self.stop_traffic_signal = False
            else:
                for i, wp in enumerate(base_waypoints):
                    p = Waypoint()
                    p.pose = wp.pose
                    p.twist.twist.linear.x = min(MAX_VEH_SPEED, wp.twist.twist.linear.x)
                    # rospy.loginfo("Decelerated Original: %s After: %s", wp.twist.twist.linear.x, p.twist.twist.linear.x)
                    updated_waypoints.append(p)
            lane.waypoints = updated_waypoints
        else:
            self.stop_traffic_signal = True
            lane.waypoints = self.decelerate_waypoints(base_waypoints, closest_idx)

        self.final_waypoints_pub.publish(lane)

    def decelerate_waypoints(self, waypoints, closest_idx):
        updated_waypoints = []
        for i, wp in enumerate(waypoints):
            p = Waypoint()
            p.pose = wp.pose

            stop_idx = max(self.stopline_wp_idx - closest_idx - 2, 0)  # Two waypoints back from line so front of car stops at line
            dist = self.distance(waypoints, i, stop_idx)
            vel = math.sqrt(2 * MAX_DECEL * dist)

            if vel < 1.:
                vel = 0.

            p.twist.twist.linear.x = min(vel, wp.twist.twist.linear.x)
            updated_waypoints.append(p)

        return updated_waypoints

    def pose_cb(self, msg):
        self.pose = msg  # around 50 Hz

    def waypoints_cb(self, waypoints):
        # load base waypoints
        self.base_waypoints = waypoints
        if not self.waypoints_2d:
            # convert waypoints to (x,y) list
            self.waypoints_2d = [
                [
                    waypoint.pose.pose.position.x,
                    waypoint.pose.pose.position.y
                ] for waypoint in waypoints.waypoints
            ]
            # build KDTree
            self.waypoint_tree = KDTree(self.waypoints_2d)

    def traffic_cb(self, msg):
        # Callback for /traffic_waypoint message
        self.stopline_wp_idx = msg.data

    def obstacle_cb(self, msg):
        # TODO: Callback for /obstacle_waypoint message. We will implement it later
        pass

    def get_waypoint_velocity(self, waypoint):
        return waypoint.twist.twist.linear.x

    def set_waypoint_velocity(self, waypoints, waypoint, velocity):
        waypoints[waypoint].twist.twist.linear.x = velocity

    def distance(self, waypoints, wp1, wp2):
        dist = 0
        dl = lambda a, b: math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2)
        for i in range(wp1, wp2 + 1):
            dist += dl(waypoints[wp1].pose.pose.position, waypoints[i].pose.pose.position)
            wp1 = i
        return dist


if __name__ == '__main__':
    try:
        WaypointUpdater()
    except rospy.ROSInterruptException:
        rospy.logerr('Could not start waypoint updater node.')
