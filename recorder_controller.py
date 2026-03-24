import os
import threading
import time
from datetime import datetime

from cameras.camera import Camera
from cameras.realsense_camera import RealSenseCamera
from cameras.device_manager import find_webcam, check_realsense


class RecorderController:

    def __init__(self):
        self.recording = False
        self.thread = None
        self.folder = ""

        self.cam1 = None
        self.cam2 = None

    def start_recording(self):

        if self.recording:
            print("Already recording")
            return

        print("Initializing cameras...")

        # Detect devices
        webcam_index = find_webcam()
        if webcam_index is None:
            raise Exception("No webcam detected")

        if not check_realsense():
            raise Exception("RealSense not detected")

        # Init cameras
        self.cam1 = Camera(webcam_index)
        self.cam2 = RealSenseCamera()

        # Create session folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.folder = os.path.join("recordings", f"session_{timestamp}")
        os.makedirs(self.folder, exist_ok=True)

        # Set RealSense output
        self.cam2.set_output_folder(self.folder)

        # Start recording
        self.cam1.start_recording(os.path.join(self.folder, "webcam.mp4"))
        self.cam2.start_recording(os.path.join(self.folder, "realsense.mp4"))

        self.recording = True

        self.thread = threading.Thread(target=self.record_loop, daemon=True)
        self.thread.start()

        print("Recording started")

    def record_loop(self):
        fps = 30
        interval = 1.0 / fps
        next_time = time.time()

        while self.recording:
            now = time.time()

            if now >= next_time:
                self.cam1.capture()
                self.cam2.capture()
                next_time += interval
            else:
                time.sleep(next_time - now)

    def stop_recording(self):

        if not self.recording:
            return

        self.recording = False

        if self.thread:
            self.thread.join()

        self.cam1.stop_recording()
        self.cam1.release()

        self.cam2.stop_recording()
        self.cam2.release()

        print(f"Saved in {self.folder}")
