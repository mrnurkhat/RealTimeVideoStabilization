# Real-Time Video Stabilization
A real-time video stabilization algorithm optimized for the Raspberry Pi 4B platform. Enables smooth video capture during recording without the need for additional hardware such as mechanical or optical stabilizers.


### About the Algorithm
The implemented algorithm is based on motion estimation using ORB keypoint matching, RANSAC filtering, and trajectory smoothing using a Kalman filter. It assumes a 2D affine motion model, which allows stabilization of horizontal and vertical translations, and rotation around the Z-axis in the image plane.

### Architecture
The system is designed following principles of modularity and object-oriented programming, making the codebase easy to maintain and extend. Thanks to this architecture, individual components can be easily replaced or scaled.

In addition to the core stabilization module, helper components provide:
* a flexible configuration API (via config.json),
* control over algorithm parameters and processing modes.

### Configuration
The program behavior is controlled by a configuration file config.json. This allows the user to adjust performance, precision, and visual output without changing the source code — making the pipeline flexible and easy to adapt to different scenarios and hardware platforms.

**Input Settings**
| Parameter              | Description                                                            | Default      |
| ---------------------- | ---------------------------------------------------------------------- | ------------ |
| `source_of_frames`     | Input source: `"camera"` or `"video"`                                  | `"camera"`   |
| `input_video_path`     | Path to input video file (required if `source_of_frames` is `"video"`) | `null`       |
| `picamera2_resolution` | Resolution when using PiCamera2                                        | `[640, 360]` |
| `picamera2_fps`        | Frames per second for PiCamera2                                        | `24`         |


### Platform Support
The software was developed and tested on:
* A laptop running Windows
* Raspberry Pi 4B running Linux (lib Picamera)
This ensures cross-platform compatibility for both desktop and embedded devices.
