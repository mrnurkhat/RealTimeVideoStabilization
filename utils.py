import cv2 as cv
import numpy as np
import json
import sys
import platform
import os

def load_and_validate_config(path):
    """
    Load configuration from a JSON file, create an empty config file if missing,
    then validate and set default parameters with proper types and value checks.
    """
    # Create empty config file if it does not exist
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({}, f)

    # Load configuration JSON
    with open(path, 'r') as f:
        config = json.load(f)

    def set_and_validate(key, default, expected_type, condition=lambda x: True, description=""):
        """
        Helper function to set default config values and validate their type and condition.
        Raises ValueError if validation fails.
        """
        value = config.setdefault(key, default)
        if not isinstance(value, expected_type) or not condition(value):
            raise ValueError(f"Invalid value for '{key}'. Expected {description}.")
        return value

     # Validate source parameter (either 'camera' or 'video')
    source = config.setdefault("source_of_frames", "camera")
    if source not in ["camera", "video"]:
        raise ValueError("Invalid value for 'source_of_frames'. Expected 'camera' or 'video'.")

    # If video source, validate video file path
    if source == "video":
        path = config.get("input_video_path")
        if not isinstance(path, str) or not path:
            raise ValueError("Invalid value for 'input_video_path'. Expected non-empty string when 'source_of_frames' = 'video'.")

    # If camera source on non-Windows systems, validate picamera2 parameters
    if source == "camera" and not IS_WINDOWS:
        res = config.setdefault("picamera2_resolution", [640, 360])
        if (
            not isinstance(res, (list, tuple)) or
            len(res) != 2 or
            not all(isinstance(x, int) and x > 0 for x in res)
        ):
            raise ValueError("Invalid value for 'picamera2_resolution'. Expected [width, height] with positive integers.")

        set_and_validate("picamera2_fps", 24, int, lambda x: x > 0, "positive integer")

    # Validate display mode flags (booleans)
    set_and_validate("display_output", True, bool, description="boolean")
    for key in ["plot_trajectory", "crop_result", "show_combined"]:
        set_and_validate(key, False, bool, description="boolean")

    # Validate margins for cropping (non-negative integers)
    set_and_validate("margin_x", 30, int, lambda x: x >= 0, "non-negative integer")
    set_and_validate("margin_y", 10, int, lambda x: x >= 0, "non-negative integer")

    # Validate stabilization parameters with ranges and types
    set_and_validate("static_scene_threshold", 0, (int, float), lambda x: x >= 0, "non-negative number")
    set_and_validate("max_feature_count", 300, int, lambda x: x > 0, "positive integer")
    set_and_validate("resize_ratio", 1.0, (int, float), lambda x: 0 < x <= 1.0, "positive number in range (0, 1]")
    
    set_and_validate("kalman_Q", 1e-5, (int, float), lambda x: x > 0, "positive number")
    set_and_validate("kalman_R", 5e-2, (int, float), lambda x: x > 0, "positive number")

    set_and_validate("max_horizontal_shift", 1000, int, lambda x: x >= 0, "non-negative integer")
    set_and_validate("max_vertical_shift", 1000, int, lambda x: x >= 0, "non-negative integer")
    set_and_validate("max_rotation", 90, int, lambda x: x >= 0, "non-negative integer")

    # Validate logging and saving options
    set_and_validate("log_message", False, bool, description="boolean")
    set_and_validate("measure_performance", False, bool, description="boolean")
    set_and_validate("save_log_to", None, (str, type(None)), description="string")

    set_and_validate("save_output_video_to", None, (str, type(None)), description="string")
    set_and_validate("output_video_fps", 25, int, lambda x: x > 0, "positive integer")

    return config


def show_result(config, frame_smooth, frame_raw):
    """
    Display the stabilized frame alongside the raw frame if configured,
    otherwise show only the stabilized frame.
    Returns whether display is on and the resulting image to be shown.
    """
    if config["show_combined"]:
        raw_h, raw_w = frame_raw.shape[:2]
        smooth_h, smooth_w = frame_smooth.shape[:2]

        if (raw_h, raw_w) != (smooth_h, smooth_w):
            # Create black background matching raw frame size
            background = np.zeros_like(frame_raw)

            # Center the stabilized frame within the background
            margin_y = (raw_h - smooth_h) // 2
            margin_x = (raw_w - smooth_w) // 2

            background[margin_y:margin_y+smooth_h, margin_x:margin_x+smooth_w] = frame_smooth
            result = np.hstack((frame_raw, background))
        else:
            result = np.hstack((frame_raw, frame_smooth))
    else:
        result = frame_smooth

    # Display preview if enabled
    if config["display_output"]:
        cv.imshow("Live", result)

    return config["display_output"], result


def crop_stabilized_frame(config, result):
    """
    Crop the stabilized frame based on configured margins to remove borders,
    returning the cropped frame. If cropping disabled, return original frame.
    """
    if not config["crop_result"]:
        return result
    
    margin_x = config["margin_x"]
    margin_y = config["margin_y"]

    h, w = result.shape[:2]
    crop_w = w - 2 * margin_x
    crop_h = h - 2 * margin_y

    if crop_w <= 0 or crop_h <= 0:
        raise ValueError("Margins too large for frame size.")

    center_x = w // 2
    center_y = h // 2

    x1 = center_x - crop_w // 2
    y1 = center_y - crop_h // 2
    x2 = x1 + crop_w
    y2 = y1 + crop_h

    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(w, x2)
    y2 = min(h, y2)

    cropped = result[y1:y2, x1:x2]

    final = np.zeros((crop_h, crop_w, 3), dtype=result.dtype)
    fy, fx = cropped.shape[:2]
    final[0:fy, 0:fx] = cropped

    return final


def init_video_writer(config, input_size):
    """
    Initialize a video writer object to save stabilized output video
    if a save path is specified. Handles output resolution based on cropping
    and combined display settings.
    """
    if config.get("save_output_video_to") is None:
        return None

    crop_result = config["crop_result"]
    show_combined = config["show_combined"]
    path = config["save_output_video_to"]
    fps = config["output_video_fps"]
    margin_x = config["margin_x"]
    margin_y = config["margin_y"]

    w, h = input_size

    # Determine output video resolution
    if show_combined:
        output_size = 2*w, h
    elif crop_result:
        output_size = w - 2 * margin_x, h - 2 * margin_y
    else:
        output_size = w, h

    # Select codec based on file extension
    if path.endswith(".avi"):
        fourcc = cv.VideoWriter_fourcc(*"XVID")
    elif path.endswith(".mp4"):
        fourcc = cv.VideoWriter_fourcc(*"mp4v")
    else:
        raise ValueError("Unsupported video format. Use '.avi' or '.mp4'.")

    return cv.VideoWriter(path, fourcc, fps, output_size)


# Platform-specific ESC key detection for graceful exit

IS_WINDOWS = platform.system() == "Windows"
if IS_WINDOWS:
    import msvcrt

    def check_exit_key():
        # Return True if ESC key is pressed (Windows)
        if msvcrt.kbhit():
            key = msvcrt.getch()
            return key == b'\x1b'
        return False

else:
    import select
    import termios
    import tty

    def check_exit_key():
        # Return True if ESC key is pressed (Linux)
        dr, _, _ = select.select([sys.stdin], [], [], 0)
        if dr:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setcbreak(fd)
                ch = sys.stdin.read(1)
                return ch == '\x1b'
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return False

def check_esc(is_display_on):
    """
    General function to check if ESC key was pressed.
    Uses OpenCV's waitKey if display window is active,
    otherwise uses platform-specific console key detection.
    """
    if is_display_on:
        return cv.waitKey(1) == 27
    else:
        return check_exit_key()
