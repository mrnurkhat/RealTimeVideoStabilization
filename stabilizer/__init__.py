import numpy as np
from .estimator import MotionEstimator
from .smoother import MotionFilter
from .transform import warp_frame


class Stabilizer:
    def __init__(self, config, first_frame, logger):
        """
        Initialize the video stabilizer with configuration parameters, the first frame,
        and a logger instance.

        Args:
            config (dict): Dictionary containing stabilization parameters.
            first_frame (ndarray): The initial video frame used for feature tracking.
            logger (Logger): Logger instance for messages and measurements.
        """
        resize_ratio = config["resize_ratio"] # Downscale factor for processing speed
        static_scene_threshold = config["static_scene_threshold"] # Threshold for skipping static scenes
        max_feature_count = config["max_feature_count"]
        max_x = config["max_horizontal_shift"] # Max allowed horizontal correction in pixels
        max_y = config["max_vertical_shift"] # Max allowed vertical correction in pixels
        max_r = np.deg2rad(config["max_rotation"]) # Max allowed rotation in radians
        Q = config["kalman_Q"]
        R = config["kalman_R"]

        self.logger = logger

        # Initialize motion estimator
        self.motion_estimator = MotionEstimator(first_frame, resize_ratio, static_scene_threshold, max_feature_count)
        
        # Initialize the Kalman filter-based motion smoother
        self.motion_filter = MotionFilter(Q, R, max_x, max_y, max_r)
        
        # Store last successfully stabilized frame
        self.last_stable = first_frame
        
        self.logger.log("Starting video stabilization...")

    def stabilize(self, curr):
        """
        Stabilizes the current frame by estimating and correcting its motion.

        Args:
            curr (ndarray): Current video frame to be stabilized.

        Returns:
            ndarray: The stabilized frame.
        """
        # Estimate raw motion between previous and current frame
        raw_motion = self.motion_estimator.estimate(curr, self.logger)

        # If motion estimation fails, return the last stabilized frame
        if raw_motion is None:
            return self.last_stable
        
        # Update motion history and apply smoothing
        self.motion_filter.cumulate(raw_motion)
        self.motion_filter.smooth()

        # Compute correction needed to stabilize the frame
        corrective_motion = self.motion_filter.compute_correction()
        
        # Apply transformation to stabilize the frame
        stabilized_frame = warp_frame(curr, corrective_motion)
        self.last_stable = stabilized_frame

        # Log frame success/failure for stats
        self.logger.update_status(raw_motion != None)

        return stabilized_frame
    
    def export_trajectory_data(self):
        """
        Exports both the raw and smoothed motion trajectories for plotting.

        Returns:
            tuple: (raw_trajectory, smoothed_trajectory)
        """
        return self.motion_filter.get_raw_and_smoothed_trajectory()