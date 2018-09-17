# CarND Capstone ROS 

## **CarND Capstone ROS Project**

The goals of this project are :
* Modify the code to follow the waypoints
* Stop at the traffic light if signal is red. 

---
### Writeup / README
This is an individual person submission. I am not part of any team. So only simulator code was implemented. This project is not fit for running on CARLA. 
Source code provided by "CarND-Capstone-carROS" was used as base for this project. 

### Modifications
File waypoint_updater.py,tl_classifier.py,tl_detector.py,twist_controller.py were modified to implement this project. 

All the required inputs for the functions to compile were fed. 

### Development Steps 
I have started with code shown in Project Walkthrough video. I have completed the functions taking ques from class and Project Walkthrough. With couple of trials i was able to compile the code without any errors , had struggled to make the vehicle follow the waypoints. After reducing the number of way ahead to 20 car was able to drive along the waypoints.

I have implemented logic in tl_classifier to identify the traffic signals. Deceleration and acceleration logics were introduced to reduce the jerky movement of the vehicle.

### Results
- Vehicle follows the waypoints and stops at the traffic lights if it is RED.

### Limitations
- Vehicle appears to be oscillating at certain points. 
