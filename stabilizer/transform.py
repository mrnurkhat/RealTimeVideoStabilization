import cv2 as cv
import numpy as np

def warp_frame(frame, corrective_motion):
    """
    Applies a 2D affine transformation (translation + rotation) to a frame
    using the provided corrective motion.

    Args:
        frame (np.ndarray): Original input frame (BGR).
        corrective_motion (tuple): (dx, dy, dtheta) in pixels and radians.

    Returns:
        np.ndarray: Warped (stabilized) frame.
    """
    h, w = frame.shape[:2]

    x = corrective_motion[0]
    y = corrective_motion[1]
    sin, cos = np.sin(corrective_motion[2]), np.cos(corrective_motion[2])
    
    # Construct 2x3 affine transformation matrix
    T_corr = np.array(
        [
            [cos, -sin, x],
            [sin, cos, y]
        ], 
        dtype=np.float32
    )

    # Apply affine transformation
    smooth_frame = cv.warpAffine(frame, T_corr, (w, h))
    
    return smooth_frame