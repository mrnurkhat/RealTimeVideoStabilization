import cv2 as cv
from collections import deque
import numpy as np
import json

def load_config(path="config.json"):
    with open(path, "r") as file:
        return json.load(file)
    

def clamp(value, min_value, max_value):
    if max_value == 0 and min_value == 0:
        return value
    return max(min_value, min(value, max_value))


def show_result(frame_smooth, frame_raw=None):
    if frame_raw is None:
        cv.imshow("Live", frame_smooth)
    else:
        if frame_raw.shape != frame_smooth.shape:
            frame_raw = cv.resize(
                frame_raw, (frame_smooth.shape[1], frame_smooth.shape[0])
            )

        combined = np.hstack((frame_raw, frame_smooth))
        cv.imshow("Live", combined)

WINDOW_SIZE = 5
abs_diff_win = deque(maxlen=WINDOW_SIZE)


def is_scene_static(curr, prev, threshold):
    curr_GS = cv.cvtColor(curr, cv.COLOR_BGR2GRAY)
    prev_GS = cv.cvtColor(prev, cv.COLOR_BGR2GRAY)

    abs_diff = cv.absdiff(curr_GS, prev_GS)
    abs_diff = np.mean(abs_diff)

    abs_diff_win.append(abs_diff)

    return len(abs_diff_win) == WINDOW_SIZE and np.mean(abs_diff_win) < threshold