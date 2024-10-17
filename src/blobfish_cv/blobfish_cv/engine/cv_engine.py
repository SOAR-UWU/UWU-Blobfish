import cv2
import numpy as np

class cv_engine:

    def __init__(self):

        self.obj_area = 0
        self.threshold = 200
        self.thresh_slider_max = 255
        self.win_title = "Obstacle Detection"
        self.track_name = "Threshold"
        self.hue = 80
        self.sub = cv2.createBackgroundSubtractorKNN()

    def thresh_process_frame(self): # <----- not in use currently
        ret, frame = self.cap.read()
        pr_frame = frame.copy()
        if ret:

            # pre-threshold
            pr_frame = cv2.GaussianBlur(frame, (9, 9), 0)
            f_mask = self.sub.apply(pr_frame)
            
            # threshold
            retval, f_thresh = cv2.threshold(f_mask, self.threshold, 255, cv2.THRESH_BINARY)

            # noise removal
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
            f_eroded = cv2.morphologyEx(f_thresh, cv2.MORPH_OPEN, kernel)

        return frame, f_eroded
    

    def hsv_processing(self, frame): # <------- currently using this method. Threshold method is there for reference only. 
        frame = frame[:, 200:1080]
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # HSV ranges
        # Blue
        ignore_lower = np.array([self.hue, 50, 50])
        ignore_higher = np.array([360, 255, 255])
        mask = cv2.inRange(hsv, ignore_lower, ignore_higher)
        mask = cv2.bitwise_not(mask)
        mask = cv2.GaussianBlur(mask, (27, 27), 0)

        # noise removal
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        return frame, mask

    def detect_contours(self, frame): 
        og, pr = self.hsv_processing(frame)
        cnt, h = cv2.findContours(pr, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        frame_out = og.copy() # <----- edit this to change which frame is displayed.

        if len(cnt) > 0:
            c = max(cnt, key=cv2.contourArea)
            
            self.obj_area = cv2.contourArea(c)
            hull = [cv2.convexHull(c, False)]
        
            cv2.drawContours(frame_out, cnt, -1, (0, 255, 0), 1, 8, h)
            cv2.drawContours(frame_out, hull, -1, (0, 0, 255), 3, 8)

        return frame_out, pr
