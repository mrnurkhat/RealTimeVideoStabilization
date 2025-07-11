import cv2 as cv

class FrameFeatures:
    def __init__(self, image, scale, orb):
        """
        Extracts ORB features from a scaled grayscale version of the input image.

        Args:
            scale (float): Scaling factor for resizing the frame.
            orb (cv.ORB): Pre-initialized OpenCV ORB feature detector.
        """
        # Resize the input image and convert it to grayscale
        self.resized_gs = cv.cvtColor(cv.resize(image, (0, 0), fx=scale, fy=scale), cv.COLOR_BGR2GRAY)

        # Detect ORB keypoints and compute descriptors
        self.kp, self.des = orb.detectAndCompute(self.resized_gs, None)