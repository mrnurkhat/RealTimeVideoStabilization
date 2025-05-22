import cv2 as cv
import numpy as np

# maybe i will add adaptive cropping

def warp_frame(frame, dx_smooth, dy_smooth, dr_smooth, crop=False):
    h, w = frame.shape[:2]

    sin, cos = np.sin(dr_smooth), np.cos(dr_smooth)
    T_smooth = np.array(
        [
            [cos, -sin, dx_smooth],
            [sin, cos, dy_smooth]
        ], 
        dtype=np.float32
    )

    smooth_frame = cv.warpAffine(frame, T_smooth, (w, h))

    if crop:
        smooth_frame = crop_stabilized_frame(smooth_frame)
    
    return smooth_frame

def crop_stabilized_frame(
    frame, width_ratio=0.05, height_ratio=0.05):
    h, w = frame.shape[:2]

    x_margin = int(w * width_ratio)
    y_margin = int(h * height_ratio)
    x_start, x_end = x_margin, w - x_margin
    y_start, y_end = y_margin, h - y_margin

    result = frame[y_start:y_end, x_start:x_end]

    return result