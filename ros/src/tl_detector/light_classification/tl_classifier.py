from styx_msgs.msg import TrafficLight
import cv2
import numpy as np

class TLClassifier(object):
    def __init__(self):
        #TODO load classifier
        self.lower_lim = np.array([0, 50, 50])
        self.upper_lim = np.array([10, 255, 255])

        self.lower_lim_2 = np.array([170, 50, 50])
        self.upper_lim_2 = np.array([180, 255, 255])



    def get_classification(self, image):
        """Determines the color of the traffic light in the image

        Args:
            image (cv::Mat): image containing the traffic light

        Returns:
            int: ID of traffic light color (specified in styx_msgs/TrafficLight)

        """
        #TODO implement light color prediction
        # Image processing using openCV
        image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        # cv2.imwrite('/home/gabymoynahan/CarND-Capstone/data/processed_images/HSV_{}.png'.format(time.time()),image_hsv)

        red_sign = cv2.inRange(image_hsv, self.lower_lim, self.upper_lim)

        red_sign2 = cv2.inRange(image_hsv, self.lower_lim_2, self.upper_lim_2)
        converted_img = cv2.addWeighted(red_sign, 1.0, red_sign2, 1.0, 0.0)
        # cv2.imwrite('/home/gabymoynahan/CarND-Capstone/data/processed_images/converted_{}.png'.format(time.time()),converted_img)
        blur_img = cv2.GaussianBlur(converted_img, (15, 15), 0)

        circles = cv2.HoughCircles(blur_img, cv2.HOUGH_GRADIENT, 0.5, 41, param1=70,
                                   param2=30, minRadius=5, maxRadius=120)

        if circles is not None:
            #rospy.loginfo("Detection TRUE")
            return TrafficLight.RED

        return TrafficLight.UNKNOWN
