from stabilizer import Stabilizer
from video_source import VideoSource
import json
import cv2 as cv
import numpy as np

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

with open("config.json") as file:
    config = json.load(file)

source = VideoSource(config)
source.initialize()

stabilizer = Stabilizer(config)

prev = source.read()

while True:
    curr = source.read()
    if curr is None:
        break

    smooth_curr = stabilizer.stabilize(prev, curr)
    prev = curr.copy()
    
    if config.get("show_combined_IO", False):
        show_result(smooth_curr, curr)
    else:
        show_result(smooth_curr)

    if cv.waitKey(1) == 27:
        break

source.release()
cv.destroyAllWindows()