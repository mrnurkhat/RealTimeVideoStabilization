# Real-Time Video Stabilization
A real-time video stabilization algorithm optimized for the Raspberry Pi 4B platform. Enables smooth video capture during recording without the need for additional hardware such as mechanical or optical stabilizers.

**Performance on Raspberry Pi 4B**
The input video `Videos/shakyTrain.mp4` has a resolution of 360p at 25 FPS.  
On a Raspberry Pi 4B with 8 GB RAM, the stabilizer processes the video with an average framerate of **~25 FPS** when output display (before/after comparison) is enabled.

This demonstrates real-time performance capability on embedded hardware.

**Demo Video**: Watch a short demo of the stabilization in action on [YouTube](https://youtu.be/tQVh7EWDGOI?si=5MEIVjK4Fql8ST39).

This project is part of my bachelor thesis. 
You can read the full thesis (in czech) on the university website:  
[Video Stabilization on Raspberry Pi](https://www.vut.cz/studenti/zav-prace/detail/167444)

### About the Algorithm
The implemented algorithm is based on motion estimation using ORB keypoint matching, RANSAC filtering, and trajectory smoothing using a Kalman filter. It assumes a 2D affine motion model, which allows stabilization of horizontal and vertical translations, and rotation around the Z-axis in the image plane.

### Architecture
The system is designed following principles of modularity and object-oriented programming, making the codebase easy to maintain and extend. Thanks to this architecture, individual components can be easily replaced or scaled.

In addition to the core stabilization module, helper components provide:
* a flexible configuration API (via config.json),
* control over algorithm parameters and processing modes.

### Project Structure
```
RealTimeVideoStabilization/
├── run.py               # Entry point of the program
├── config.json          # Main configuration file for the stabilization pipeline
├── source.py            # Handles input source selection: camera or video file
├── logger.py            # Logging and performance measurement utilities
├── visualizer.py        # Real-time display and trajectory plotting tools
├── utils/               # Auxiliary utilities (e.g., image transformations)
│
├── stabilizer/          # Core stabilization logic (modular algorithm components)
│   ├── __init__.py
│   ├── estimator.py     # Motion estimation using keypoints and RANSAC
│   ├── frame_features.py# ORB feature detection and matching
│   ├── smoother.py      # Kalman filter or alternative smoothing
│   ├── transform.py     # Affine transform building and limiting
│
├── Videos/              # Sample input videos (e.g., shaky footage for testing)
│   ├── .gitkeep         # Keeps the folder in Git (if empty)
│   ├── shakyTrain.mp4   # Example shaky input video
│
├── .gitignore           # Files and folders to exclude from Git tracking
├── LICENSE              # Project license (MIT)
└── README.md            # Project documentation
```

### Configuration
The program behavior is controlled by a configuration file config.json. This allows the user to adjust performance, precision, and visual output without changing the source code — making the pipeline flexible and easy to adapt to different scenarios and hardware platforms.

**Input Settings**
| Parameter              | Description                                                            | Default      |
| ---------------------- | ---------------------------------------------------------------------- | ------------ |
| `source_of_frames`     | Input source: `"camera"` or `"video"`                                  | `"camera"`   |
| `input_video_path`     | Path to input video file (required if `source_of_frames` is `"video"`) | `null`       |
| `picamera2_resolution` | Resolution when using PiCamera2                                        | `[640, 360]` |
| `picamera2_fps`        | Frames per second for PiCamera2                                        | `24`         |

Parameters for PiCamera2 are relevant only on non-Windows platform and when source_of_frames = "camera".

**Display Options**
| Parameter         | Description                                      | Default |
| ----------------- | ------------------------------------------------ | ------- |
| `display_output`  | Show output frames in real-time                  | `true`  |
| `show_combined`   | Show original and stabilized frames side-by-side | `false` |
| `crop_result`     | Enable cropping to remove border artifacts       | `false` |
| `margin_x`        | Crop margin (left/right in pixels)               | `30`    |
| `margin_y`        | Crop margin (top/bottom in pixels)               | `10`    |
| `plot_trajectory` | Show estimated camera trajectory as a plot       | `false` |

**Stabilization Parameters**
| Parameter                | Description                                                          | Default |
| ------------------------ | -------------------------------------------------------------------- | ------- |
| `static_scene_threshold` | Threshold for detecting a static scene (0 disables detection)        | `0`     |
| `max_feature_count`      | Maximum number of ORB keypoints to track per frame                   | `300`   |
| `resize_ratio`           | Image downscale factor before feature detection (speed vs. accuracy) | `1.0`   |
| `kalman_Q`               | Process noise variance in Kalman filter                              | `1e-5`  |
| `kalman_R`               | Measurement noise variance in Kalman filter                          | `0.05`  |
| `max_horizontal_shift`   | Maximum allowed horizontal correction shift (in px)                  | `1000`  |
| `max_vertical_shift`     | Maximum allowed vertical correction shift (in px)                    | `1000`  |
| `max_rotation`           | Maximum allowed rotational correction (in degrees)                   | `90`    |

**Logging & Output**
| Parameter              | Description                                        | Default |
| ---------------------- | -------------------------------------------------- | ------- |
| `log_message`          | Enable logging of internal messages                | `false` |
| `measure_performance`  | Measure and log processing time per frame          | `false` |
| `save_log_to`          | Path to save logs (if not set, logs are not saved) | `null`  |
| `save_output_video_to` | Path to save the output stabilized video           | `null`  |
| `output_video_fps`     | Frame rate of the output video                     | `25`    |

### Platform Support
The software was developed and tested on:
* A laptop running Windows
* Raspberry Pi 4B running Linux (lib Picamera)
This ensures cross-platform compatibility for both desktop and embedded devices.

### Running the Project
Clone the repository:
```
git clone https://github.com/mrnurkhat/RealTimeVideoStabilization.git
cd RealTimeVideoStabilization
```

Install dependencies:

```
pip install -r requirements.txt
```

If you plan to run the project on a Raspberry Pi, additionally install the PiCamera2 dependency:

```
pip install -r requirements-pi.txt
```

Run the stabilizer:

```
python main.py
```

**Note for Non-Windows Users**

If you are running this code on a non-Windows system (e.g. Linux or macOS), and do not use a Raspberry Pi camera, you need to manually disable the PiCamera2 module to avoid import errors.

Please modify the file source.py as follows:

Replace line 7:
```
from picamera2 import Picamera2
```
With:
```
Picamera2 = None
```
This ensures compatibility when running the code without PiCamera2 installed or supported.

### License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

