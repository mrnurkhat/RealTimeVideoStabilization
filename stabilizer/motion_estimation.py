from scene_analysis import is_scene_static
import cv2 as cv
import numpy as np

orb = cv.ORB_create(nfeatures=200)
bfm = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=True)

def estimate_motion(prev, curr, max_translation=30, max_rotation=np.deg2rad(10), verbose=False):
    if is_scene_static(prev, curr):
        return 0, 0, 0

    prev_kp, prev_des = orb.detectAndCompute(prev, None)
    curr_kp, curr_des = orb.detectAndCompute(curr, None)

    if prev_des is None or curr_des is None:
        if verbose:
            print("Descriptor(s) is None.")
        return None
    
    matches = bfm.match(prev_des, curr_des)

    if len(matches) < 10:
        if verbose:
            print("Too few matches.")
        return None
    
    matches = sorted(matches, key=lambda x: x.distance)

    prev_pts = np.float32([prev_kp[m.queryIdx].pt for m in matches]).reshape(
        -1, 1, 2
    )
    curr_pts = np.float32([curr_kp[m.trainIdx].pt for m in matches]).reshape(
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