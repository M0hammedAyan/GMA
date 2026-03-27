# Dual Camera Recording System (GMA Project)

## Overview

This module records video simultaneously from two cameras connected to a Raspberry Pi.
The recorded videos are saved in a session folder and will later be used for analysis by a machine learning model.

The system is designed to be controlled through a simple PySide6 UI with **Start Recording** and **Stop Recording** buttons.

---

## Hardware Used

* Raspberry Pi
* Lenovo FHD USB Webcam
* See3CAM Stereo Camera

Detected devices:

| Device         | Video Node    |
| -------------- | ------------- |
| Lenovo Webcam  | `/dev/video0` |
| See3CAM Stereo | `/dev/video2` |

---

## Video Configuration

| Parameter  | Value                                    |
| ---------- | ---------------------------------------- |
| Resolution | **640 × 480**                            |
| Frame Rate | **30 FPS**                               |
| Format     | **BGR3 (converted to MJPG for storage)** |

This configuration is chosen because it is stable when recording from two cameras on Raspberry Pi.

---

## Project Structure

```
GMA/
│
├── main.py
├── recorder.py
├── sync_multicam_capture.py
├── view_recordings.py
├── cameras/
├── recordings/
└── README.md
```

---

## How to Run

1. Activate the environment

```
uv run main.py
```

or

```
python main.py
```

2. The UI window will appear.

3. Click **Start Recording** to begin recording.

4. Click **Stop Recording** to stop recording and save the videos.

Optional: set a custom output root directory before launch.

```
export GMA_RECORDINGS_DIR=/path/to/your/domain/folder
python main.py
```

To reduce dropped frames on Raspberry Pi and keep recorded video duration close to real time,
you can tune capture/export load:

```
export GMA_CAPTURE_FPS=10
export GMA_SAVE_RGB_DEPTH_EVERY=5
export GMA_SAVE_POINTCLOUD_EVERY=20
python main.py
```

Meaning:
* `GMA_CAPTURE_FPS`: target video FPS used by both writers and capture loop
* `GMA_SAVE_RGB_DEPTH_EVERY`: save RGB/Depth arrays every N frames
* `GMA_SAVE_POINTCLOUD_EVERY`: save pointcloud NPZ every N frames (heaviest step)

Note: the UI timer starts only after camera pipelines are fully initialized, so displayed
recording time now matches actual captured duration.

You can also run the lightweight synchronized CLI recorder:

```
python sync_multicam_capture.py
```

For Raspberry Pi stability, capture FPS is intentionally low by default (`10`) and can be set to `9` or `8`:

```
python sync_multicam_capture.py --fps 10
python sync_multicam_capture.py --fps 9
python sync_multicam_capture.py --fps 8
```

If your RealSense firmware does not support 10/9/8 at 640x480, the recorder automatically
falls back to a compatible profile (for example 15 or 30) so recording still starts.

---

## Playback Viewer

Use the viewer to play:
* RealSense RGB
* Webcam RGB
* Depth colormap
* Optional NPZ point cloud (Open3D)

Examples:

```
python view_recordings.py
python view_recordings.py --session recordings/session_YYYYMMDD_HHMMSS
python view_recordings.py --session recordings/session_YYYYMMDD_HHMMSS --pointcloud
python view_recordings.py --session recordings/session_YYYYMMDD_HHMMSS --fps 10
```

Note: when `--session` is not provided, the viewer now picks the latest playable session
(it automatically skips empty/incomplete newest session folders).

Viewer controls:
* `q` = quit
* `space` = pause/resume
* `n` = next frame (when paused)

Playback note:
* For sessions recorded by `main.py`, the viewer uses `realsense.avi/.mp4` as the timeline,
  so playback duration matches the real recorded duration even when depth/pointcloud files
  are saved every N frames.

---

## Output

Videos are saved in a session folder:

```
recordings/
   session_YYYYMMDD_HHMMSS/
    realsense.avi
    webcam.avi
        realsense/
            rgb/*.png
            depth/*.npy
            pointcloud/*.npz
```

Each session contains synchronized recordings from both cameras.

---

## Current Features

* Dual camera recording
* Threaded video capture
* Session-based storage
* Simple UI control
* Raspberry Pi compatible

---

## Future Work

* Video encryption before transfer
* API integration with backend server
* Automatic upload of recorded videos
* Machine learning analysis pipeline
* Automated report generation
