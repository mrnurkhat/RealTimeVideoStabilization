import cv2 as cv
import time
import os
import platform

IS_WINDOWS = platform.system() == "Windows"

if not IS_WINDOWS:
    from picamera2 import Picamera2
else:
    Picamera2 = None

class VideoSource:
    def __init__(self, config):
        self.config = config
        self.capture = None
        self.picam2 = None

    def initialize(self):
        if self.config["input_source"] == "video":
            video_path = self.config["video_path"]
            self.capture = cv.VideoCapture(video_path)
            if not self.capture.isOpened():
                raise IOError(f"Failed to open video file: {video_path}")

        elif self.config["input_source"] == "camera":
            if self.config["camera_backend"] == "cv2":
                self.capture = cv.VideoCapture(0)
                if not self.capture.isOpened():
                    raise IOError("Failed to open camera using OpenCV")

                self.capture.set(cv.CAP_PROP_FRAME_WIDTH, self.config["resolution"][0])
                self.capture.set(cv.CAP_PROP_FRAME_HEIGHT, self.config["resolution"][1])
                self.capture.set(cv.CAP_PROP_FPS, self.config["fps"])

            elif self.config["camera_backend"] == "picamera2":
                if IS_WINDOWS:
                    raise RuntimeError("Picamera2 is only supported on Raspberry Pi")
                try:
                    self.picam2 = Picamera2()
                    video_config = self.picam2.create_video_configuration(
                        main={
                            "size": tuple(self.config["resolution"]),
                            "format": "RGB888",
                        },
                        controls={"FrameRate": self.config["fps"]},
                    )
                    self.picam2.configure(video_config)
                    self.picam2.start()
                    time.sleep(1)
                except Exception as e:
                    raise RuntimeError(f"Failed to initialize Picamera2: {e}")

            else:
                raise ValueError(
                    f"Unknown camera backend: {self.config['camera_backend']}"
                )

        else:
            raise ValueError(f"Unknown input source: {self.config['input_source']}")

    def read(self):
        if self.capture:
            ret, frame = self.capture.read()
            if not ret:
                print("Failed to read frame")
            return frame
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
        if self.capture:
            self.capture.release()
        if self.picam2:
            self.picam2.close()
