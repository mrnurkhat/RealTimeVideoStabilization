import cv2 as cv
import numpy as np
from .motion_estimation import estimate_motion, FrameFeatures
from .trajectory_smoothing import TrajectorySmoother
from .warping import warp_frame
from plot_trajectory import PlotTrajectory
from utils import clamp, is_scene_static

orb = cv.ORB_create(nfeatures=200)
bfm = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=True)

class Stabilizer:
    def __init__(self, config, prev):
        self.prev_ff = FrameFeatures(prev, orb)

        self.config = config
        self.width = config["resolution"][0]
        self.height = config["resolution"][1]

        self.max_x_ratio = config.get("max_horizontal_translation_ratio", 0)
        self.max_y_ratio = config.get("max_vertical_translation_ratio", 0)
        self.max_rot = config.get("max_rotation_degree", 0)

        self.plotter = PlotTrajectory(config.get("show_trajectory", False))
        
        self.smoother = TrajectorySmoother(
            Q=config.get("kalman_Q", 5e-5),
            R=config.get("kalman_R", 3e-2),
            )
        
    def stabilize(self, curr):
        curr_ff = FrameFeatures(curr, orb)

        if is_scene_static(self.prev_ff.image, curr_ff.image, self.config.get("static_threshold", 1.0)):
            motion = (0, 0, 0)
        else:
            motion = estimate_motion(self.prev_ff, curr_ff, bfm, verbose=False)

        self.prev_ff = curr_ff

        if motion is None:
            return None
        
        dx_raw, dy_raw, dr_raw = motion

        x_raw_sum, y_raw_sum, r_raw_sum = self.smoother.cumulate(dx_raw, dy_raw, dr_raw)
        x_smooth_sum, y_smooth_sum, r_smooth_sum = self.smoother.smooth()

        self.plotter.collect(
            x_raw_sum, y_raw_sum, r_raw_sum,
            x_smooth_sum, y_smooth_sum, r_smooth_sum
        )

        if (dx_raw, dy_raw, dr_raw) == (0, 0, 0):
            return curr

        max_dx = self.width * self.max_x_ratio
        max_dy = self.height * self.max_y_ratio
        max_dr = np.deg2rad(self.max_rot)

        dx_corr = clamp((x_smooth_sum - x_raw_sum), -max_dx, max_dx)
        dy_corr = clamp((y_smooth_sum - y_raw_sum), -max_dy, max_dy)
        dr_corr = clamp((r_smooth_sum - r_raw_sum), -max_dr, max_dr)

        smooth_curr = warp_frame(curr, dx_corr, dy_corr, dr_corr, self.config.get("crop_frame", False))

        return smooth_curr
    
    def display_trajectory(self):
        self.plotter.display()



        