import os
import threading
import time
from datetime import datetime

from cameras.camera import Camera
from cameras.realsense_camera import RealSenseCamera


class RecorderController:

    def __init__(self):
        self.recording = False
        self.thread = None
        self.folder = ""

        self.cam1 = None  # Webcam
        self.cam2 = None  # RealSense

    def start_recording(self):

        if self.recording:
            print("Recording already running")
            return

        print("Using webcam + RealSense")

        try:
            # Webcam (OpenCV)
            self.cam1 = Camera(6)

            # RealSense (pyrealsense2)
            self.cam2 = RealSenseCamera()

        except Exception as e:
            print("Camera init failed:", e)
            return

        # Create session folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.folder = os.path.join("recordings", f"session_{timestamp}")
        os.makedirs(self.folder, exist_ok=True)

        # Start recording
        self.cam1.start_recording(os.path.join(self.folder, "webcam.mp4"))
        self.cam2.start_recording(os.path.join(self.folder, "realsense.mp4"))

        self.recording = True

        # Start recording thread
        self.thread = threading.Thread(target=self.record_loop, daemon=True)
        self.thread.start()

        print("Recording started")

    def record_loop(self):

        target_fps = 10
        frame_interval = 1.0 / target_fps

        next_frame_time = time.time()

        while self.recording:

            now = time.time()

            if now >= next_frame_time:

                if self.cam1:
                    self.cam1.capture()

                if self.cam2:
                    self.cam2.capture()

                # schedule next frame EXACTLY
                next_frame_time += frame_interval

            else:
                # sleep only the remaining time
                time.sleep(next_frame_time - now)

    def stop_recording(self):

        if not self.recording:
            print("Recording not running")
            return

        self.recording = False

        if self.thread:
            self.thread.join()

        # Stop webcam
        if self.cam1:
            self.cam1.stop_recording()
            self.cam1.release()

        # Stop RealSense
        if self.cam2:
            self.cam2.stop_recording()
            self.cam2.release()

        print("Recording saved in:", self.folder)
