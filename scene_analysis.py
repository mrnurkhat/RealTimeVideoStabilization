import cv2 as cv
from collections import deque
import numpy as np

WINDOW_SIZE = 5
abs_diff_win = deque(maxlen=WINDOW_SIZE)


def is_scene_static(curr, prev, threshold):
    curr_GS = cv.cvtColor(curr, cv.COLOR_BGR2GRAY)
    prev_GS = cv.cvtColor(prev, cv.COLOR_BGR2GRAY)

    abs_diff = cv.absdiff(curr_GS, prev_GS)
    abs_diff = np.mean(abs_diff)

    abs_diff_win.append(abs_diff)

    return len(abs_diff_win) == WINDOW_SIZE and np.mean(abs_diff_win) < threshold