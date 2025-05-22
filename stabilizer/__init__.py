import cv2 as cv
import numpy as np
from .motion_estimation import estimate_motion
from .trajectory_smoothing import TrajectorySmoother
from .warping import warp_frame
from utils import clamp

class Stabilizer:
    def __init__(self, config):
        self.config = config
        self.width = config["resolution"][0]
        self.height = config["resolution"][1]
        self.max_x_ratio = config.get("max_horizontal_translation_ratio", 0)
        self.max_y_ratio = config.get("max_vertical_translation_ratio", 0)
        self.max_rot = config.get("max_rotation_degree", 0)
        
        self.smoother = TrajectorySmoother(
            Q=config.get("kalman_Q", 5e-5),
            R=config.get("kalman_R", 3e-2),
            enable_plot=config.get("show_trajectory", False)
            )
        
    def stabilize(self, prev, curr):
        motion = estimate_motion(prev, curr, verbose=True)
        if motion is None:
            return curr
        
        dx_raw, dy_raw, dr_raw = motion

        dx_smooth, dy_smooth, dr_smooth = self.smoother.smooth(dx_raw, dy_raw, dr_raw)

        dx_corr = clamp((dx_smooth - dx_raw), -self.width * self.max_x_ratio, self.width * self.max_x_ratio)
        dy_corr = clamp((dy_smooth - dy_raw), -self.height * self.max_y_ratio, self.height * self.max_y_ratio)
        dr_corr = clamp((dr_smooth - dr_raw), np.deg2rad(-self.max_rot), np.deg2rad(self.max_rot))

        smooth_curr = warp_frame(curr, dx_corr, dy_corr, dr_corr, self.config.get("crop_frame", False))

        return smooth_curr
    
    def display_trajectory(self):
        self.smoother.display_trajectory()



        