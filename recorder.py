import os
import threading
import time
from datetime import datetime

from cameras.webcam import Webcam
from cameras.realsense import RealSenseCamera
from cameras.device_manager import find_webcam, check_realsense


class Recorder:

    def __init__(self, output_root=None):
        self.running = False
        self.thread = None
        self.realsense = None
        self.webcam = None
        self.session = None
        self.last_error = None
        self.output_root = output_root or os.getenv("GMA_RECORDINGS_DIR", "recordings")
        self.capture_fps = max(1, int(os.getenv("GMA_CAPTURE_FPS", "10")))

    def start(self):
        if self.running:
            return

        self.last_error = None

        if not check_realsense():
            raise Exception("RealSense not detected")

        webcam_device = find_webcam()
        if webcam_device is None:
            raise Exception("No webcam detected")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_path = os.path.join(self.output_root, f"session_{timestamp}")

        try:
            # RealSense first to avoid OpenCV probing/locking RealSense V4L2 nodes.
            self.realsense = RealSenseCamera()
            self.webcam = Webcam(webcam_device)

            os.makedirs(session_path, exist_ok=True)
            self.realsense.setup_folders(session_path)

            self.realsense.start(os.path.join(session_path, "realsense.avi"), video_fps=self.capture_fps)
            self.webcam.start(os.path.join(session_path, "webcam.avi"), video_fps=self.capture_fps)
        except Exception:
            self.stop()
            raise

        self.session = session_path

        self.running = True
        self.thread = threading.Thread(target=self.loop, daemon=True)
        self.thread.start()

        print("Recording started")

    def loop(self):
        fps = self.capture_fps
        interval = 1.0 / fps
        next_time = time.monotonic()

        while self.running:
            now = time.monotonic()

            if now >= next_time:
                try:
                    if self.realsense is not None:
                        self.realsense.capture()
                    if self.webcam is not None:
                        self.webcam.capture()
                except Exception as err:
                    self.last_error = err
                    self.running = False
                    break

                # Avoid runaway drift when one cycle takes too long.
                next_time = max(next_time + interval, now)
            else:
                time.sleep(next_time - now)

    def stop(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join()
        self.thread = None

        if self.webcam is not None:
            try:
                self.webcam.stop()
            finally:
                self.webcam = None

        if self.realsense is not None:
            try:
                self.realsense.stop()
            finally:
                self.realsense = None

        if self.session:
            print("Saved:", self.session)
            self.session = None
