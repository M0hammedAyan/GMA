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
├── recorder_controller.py
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

---

## Output

Videos are saved in a session folder:

```
recordings/
   session_YYYYMMDD_HHMMSS/
        cam1.avi
        cam2.avi
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
