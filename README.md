# Color-Only Recording System (GMA Project)

## Overview

This project records the RealSense RGB stream in a PySide6 application and saves each session to disk. Depth capture, depth visualization, and point cloud export have been removed for stability.

## Hardware

* Raspberry Pi
* Intel RealSense device with an RGB sensor

## Video Configuration

| Parameter | Value |
| --- | --- |
| Resolution | 1280 x 720 |
| Frame Rate | 30 FPS, with 15 FPS fallback |
| Format | BGR8 stored as AVI using MJPG or XVID |

## Run

```bash
python main.py
```

Run the minimal single-button Qt launcher:

```bash
python main.py --button-gui
```

Run with the full frontend UI:

```bash
python run_with_frontend.py
```

Run without frontend (headless recorder):

```bash
python run_without_frontend.py
```

Optional environment variable:

```bash
export GMA_RECORDINGS_DIR=/path/to/recordings
```

## Output

Each session is stored under:

```text
recordings/
  session_YYYYMMDD_HHMMSS/
    realsense.avi
    realsense/
      rgb/
```

## Viewer

Play the latest session or a specific session folder:

```bash
python view_recordings.py
python view_recordings.py --session recordings/session_YYYYMMDD_HHMMSS
```

## Notes

* The camera pipeline uses only `rs.stream.color`.
* Recording uses one writer and initializes it after the first frame.
* The UI preview shows the live color frame only.
* Running `python main.py` now starts the raw/headless recorder.
* `--button-gui` opens a minimal single-button Qt window for start/stop control.
