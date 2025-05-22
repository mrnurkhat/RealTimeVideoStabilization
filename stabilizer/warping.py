import cv2 as cv
import numpy as np

# maybe i will add adaptive cropping

def warp_frame(frame, dx_corr, dy_corr, dr_corr, crop=False):
    h, w = frame.shape[:2]

    sin, cos = np.sin(dr_corr), np.cos(dr_corr)
    T_corr = np.array(
        [
            [cos, -sin, dx_corr],
            [sin, cos, dy_corr]
        ], 
        dtype=np.float32
    )

    smooth_frame = cv.warpAffine(frame, T_corr, (w, h))

    if crop:
        smooth_frame = crop_stabilized_frame(smooth_frame, )
    
    return smooth_frame

def crop_stabilized_frame(
    frame, width_ratio=0.15, height_ratio=0.10):
    h, w = frame.shape[:2]

    x_margin = int(w * width_ratio)
    y_margin = int(h * height_ratio)
    x_start, x_end = x_margin, w - x_margin
    y_start, y_end = y_margin, h - y_margin

    result = frame[y_start:y_end, x_start:x_end]

    return result