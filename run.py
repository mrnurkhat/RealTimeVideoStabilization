from stabilizer import Stabilizer
from video_source import VideoSource
import cv2 as cv
import utils

config = utils.load_config()

source = VideoSource(config)
source.initialize()

prev = source.read()
stabilizer = Stabilizer(config, prev)

while True:
    curr = source.read()
    if curr is None:
        break

    smooth_curr = stabilizer.stabilize(curr)
    prev = curr.copy()

    if smooth_curr is None:
        continue
    
    if config.get("show_combined_IO", False):
        utils.show_result(smooth_curr, curr)
    else:
        utils.show_result(smooth_curr)

    if cv.waitKey(1) == 27:
        break

source.release()
cv.destroyAllWindows()

stabilizer.display_trajectory()