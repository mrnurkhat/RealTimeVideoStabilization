import cv2 as cv
import time
from utils import IS_WINDOWS

# Import Picamera2 only if not running on Windows
if not IS_WINDOWS:
    Picamera2 = None#from picamera2 import Picamera2
else:
    Picamera2 = None

class FrameSource:
    def __init__(self, config):
        self.capture = None
        self.picam2 = None

        # Select the source of frames: video file or live camera
        if config["source_of_frames"] == "video":
            video_path = config["input_video_path"]
            self.capture = cv.VideoCapture(video_path)
            if not self.capture.isOpened():
                raise IOError(f"Failed to open video file: {video_path}")

        elif config["source_of_frames"] == "camera":
            # Use OpenCV VideoCapture on Windows
            if IS_WINDOWS:
                self.capture = cv.VideoCapture(0)
                if not self.capture.isOpened():
                    raise IOError("Failed to open camera using OpenCV")
            # Use Picamera2 on non-Windows platforms (e.g., Raspberry Pi)
            else:
                try:
                    self.picam2 = Picamera2()
                    video_config = self.picam2.create_video_configuration(
                        main={
                            "size": tuple(config["picamera2_resolution"]),
                            "format": "RGB888",
                        },
                        controls={"FrameRate": config["picamera2_fps"]},
                    )
                    self.picam2.configure(video_config)
                    self.picam2.start()
                    time.sleep(1) # Allow camera to warm up
                except Exception as e:
                    raise RuntimeError(f"Failed to initialize Picamera2: {e}")
        else:
            raise ValueError(f"Unknown input source: {config['source_of_frames']}")

    def read(self):
        # Read frame from OpenCV VideoCapture
        if self.capture:
            ret, frame = self.capture.read()
            if not ret:
                print("Failed to read frame")
            return frame
        # Read a frame from Picamera2
        elif self.picam2:
            try:
                frame = self.picam2.capture_array()
                return frame
            except Exception as e:
                print(f"Error capturing frame from Picamera2: {e}")
                return None
        else:
            print("Video source is not initialized.")
            return None

    def release(self):
        # Release resources
        if self.capture:
            self.capture.release()
        if self.picam2:
            self.picam2.stop()