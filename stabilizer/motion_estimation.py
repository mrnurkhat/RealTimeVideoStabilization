import cv2 as cv
import numpy as np

class FrameFeatures:
    def __init__(self, image, orb):
        self.image = image
        self.kp, self.des = orb.detectAndCompute(image, None)

def estimate_motion(prev: FrameFeatures, curr: FrameFeatures, bfm, max_translation=50, max_rotation=np.deg2rad(10), verbose=False):
    if prev.des is None or curr.des is None:
        if verbose:
            print("Descriptor(s) is None.")
        return None
    
    matches = bfm.match(prev.des, curr.des)

    if len(matches) < 10:
        if verbose:
            print("Too few matches.")
        return None
    
    matches = sorted(matches, key=lambda x: x.distance)

    prev_pts = np.float32([prev.kp[m.queryIdx].pt for m in matches]).reshape(
        -1, 1, 2
    )
    curr_pts = np.float32([curr.kp[m.trainIdx].pt for m in matches]).reshape(
        -1, 1, 2
    )

    T_raw, inlies = cv.estimateAffine2D(prev_pts, curr_pts, method=cv.RANSAC)

    if T_raw is None or not np.isfinite(T_raw).all():
        if verbose:
            print("Estimated affine transform is not valid.")
        return None
    
    if inlies is None or np.sum(inlies) < 10:
        if verbose:
            print("Too few inliers — skipping the frame.")
        return None
    
    dx_raw = T_raw[0, 2]
    dy_raw = T_raw[1, 2]
    dr_raw = np.arctan2(T_raw[1, 0], T_raw[0, 0])

    if np.hypot(dx_raw, dy_raw) > max_translation or abs(dr_raw) > max_rotation:
        if verbose:
            print("Abnormal transformation — skipping a frame.")
        return None
    
    if verbose:
        print(f"Matches: {len(matches)}, Inliers: {np.sum(inlies)}")

    return dx_raw, dy_raw, dr_raw