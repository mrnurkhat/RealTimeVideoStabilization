import cv2 as cv
import numpy as np
from .frame_features import FrameFeatures
from collections import deque


class MotionEstimator:
    def __init__(self, first_frame, resize_ratio, static_scene_threshold, max_feature_count):
        """
        Initializes the motion estimator using ORB feature detection and affine transformation.

        Args:
            first_frame (ndarray): The initial frame to track motion from.
            resize_ratio (float): Ratio to downscale frames for faster processing.
            static_scene_threshold (float): Threshold for detecting if the scene is static.
            max_feature_count (int): Maximum number of ORB features to detect per frame.
        """
        self.orb = cv.ORB_create(nfeatures=max_feature_count)
        self.bfm = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=True)
        self.resize_ratio = resize_ratio

        # Extract features from the first frame
        self.prev = FrameFeatures(first_frame, resize_ratio, self.orb)

        # Threshold to decide whether the scene is static
        self.static_scene_threshold = static_scene_threshold

         # Moving window of absolute frame differences for static scene detection
        self.abs_diff_win = deque(maxlen=10)

        # Tracks whether the previous state was static
        self.was_static = False

    def estimate(self, curr_frame, logger):
        """
        Estimates 2D motion (translation + rotation) between the current and previous frame.

        Args:
            curr_frame (ndarray): The new frame to compare against the previous one.
            logger (Logger): Logger instance to report warnings and scene status.

        Returns:
            tuple or None: (dx, dy, dr) motion or None if estimation failed.
        """
         # Extract keypoints and descriptors for the current frame
        curr = FrameFeatures(curr_frame, self.resize_ratio, self.orb)

        # Check descriptor validity
        if self.prev.des is None or curr.des is None:
            logger.log("Descriptor(s) is None.", "WARN")
            return None
        
         # Match descriptors between previous and current frame
        matches = self.bfm.match(self.prev.des, curr.des)
        if len(matches) < 10:
            logger.log("Too few matches.", "WARN")
            self.prev = curr
            return None
        
         # Sort matches by descriptor distance (smaller is better)
        matches = sorted(matches, key=lambda x: x.distance)

         # Extract matched keypoint coordinates
        prev_pts = np.float32([self.prev.kp[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        curr_pts = np.float32([curr.kp[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
        
        # Estimate affine transformation using RANSAC to filter outliers
        T_raw, inlies = cv.estimateAffine2D(prev_pts, curr_pts, method=cv.RANSAC)

        # Validate the transform
        if T_raw is None or not np.isfinite(T_raw).all():
            logger.log("Estimated affine transform is not valid.", "WARN")
            self.prev = curr
            return None
        
        if inlies is None or np.sum(inlies) < 10:
            logger.log("Too few inliers — skipping the frame.", "WARN")
            self.prev = curr
            return None

         # Extract translation and rotation from the transform
        dx_raw = T_raw[0, 2]
        dy_raw = T_raw[1, 2]
        dr_raw = np.arctan2(T_raw[1, 0], T_raw[0, 0])

        # Scale translation back to original resolution
        dx_raw /= self.resize_ratio
        dy_raw /= self.resize_ratio

        # Detect static scene using mean absolute difference
        if self.is_static_scene(curr):
            self.prev = curr
            self.last_valid_motion = 0, 0, 0
            if not self.was_static:
                logger.log("Static scene detected.")
                self.was_static = True
            return 0, 0, 0

        if self.was_static:
            logger.log("Dynamic scene detected.")
            self.was_static = False

        self.prev = curr
        return dx_raw, dy_raw, dr_raw
    
    def is_static_scene(self, curr):
        """
        Determines if the scene is static based on grayscale frame difference.

        Args:
            curr (FrameFeatures): Features of the current frame.

        Returns:
            bool: True if scene is considered static.
        """
        # Compute absolute difference between grayscale resized frames
        abs_diff = cv.absdiff(curr.resized_gs, self.prev.resized_gs)
        abs_diff = np.mean(abs_diff)

        # Add to moving average window
        self.abs_diff_win.append(abs_diff)

        # Return True if enough values are available and mean is low
        is_full = len(self.abs_diff_win) == self.abs_diff_win.maxlen
        return is_full and np.mean(self.abs_diff_win) < self.static_scene_threshold