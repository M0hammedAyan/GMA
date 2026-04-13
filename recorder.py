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
        self.webcam_thread = None
        self.realsense = None
        self.webcam = None
        self.session = None
        self.last_error = None
        self.output_root = output_root or os.getenv("GMA_RECORDINGS_DIR", "recordings")
        self.capture_fps = max(1, int(os.getenv("GMA_CAPTURE_FPS", "10")))
        self.profile_capture = os.getenv("GMA_PROFILE_CAPTURE", "0") == "1"
        self._profile_lock = threading.Lock()
        self._profile_started_at = None
        self._webcam_frames = 0
        self._last_profile_log = 0.0

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

            # Keep capture pacing and both video writers on one shared effective FPS.
            sensor_fps = int(getattr(self.realsense, "sensor_fps", self.capture_fps))
            self.capture_fps = max(1, min(self.capture_fps, sensor_fps))

            os.makedirs(session_path, exist_ok=True)
            self.realsense.setup_folders(session_path)

            self.realsense.start(os.path.join(session_path, "realsense.avi"), video_fps=self.capture_fps)
            self.webcam.start(os.path.join(session_path, "webcam.avi"), video_fps=self.capture_fps)
        except Exception:
            self.stop()
            raise

        self.session = session_path

        self.running = True
        self._profile_started_at = time.monotonic()
        self._last_profile_log = self._profile_started_at
        self._webcam_frames = 0

        self.webcam_thread = threading.Thread(target=self._webcam_loop, daemon=True)
        self.webcam_thread.start()

        print("Recording started")

    def _log_profile(self):
        if not self.profile_capture:
            return

        with self._profile_lock:
            now = time.monotonic()
            if now - self._last_profile_log < 5.0:
                return

            elapsed = max(1e-6, now - self._profile_started_at)
            webcam_fps = self._webcam_frames / elapsed
            print(f"Capture stats: webcam={webcam_fps:.2f} fps")
            self._last_profile_log = now

    def _webcam_loop(self):
        interval = 1.0 / float(self.capture_fps)
        next_time = time.monotonic()

        while self.running:
            if self.realsense is not None and self.realsense.last_error is not None:
                self.last_error = self.realsense.last_error
                self.running = False
                break

            now = time.monotonic()
            if now < next_time:
                time.sleep(next_time - now)
                continue

            try:
                if self.webcam is not None:
                    self.webcam.capture()
                    self._webcam_frames += 1
                    self._log_profile()
            except Exception as err:
                self.last_error = err
                self.running = False
                break

            next_time = max(next_time + interval, time.monotonic())

    def stop(self):
        self.running = False
        if self.webcam_thread and self.webcam_thread.is_alive():
            self.webcam_thread.join()
        self.webcam_thread = None

        if self.webcam is not None:
            try:
                self.webcam.stop()
            finally:
                self.webcam = None

        if self.realsense is not None:
            try:
                self.realsense.stop()
                if self.last_error is None and self.realsense.last_error is not None:
                    self.last_error = self.realsense.last_error
            finally:
                self.realsense = None

        if self.session:
            print("Saved:", self.session)
            self.session = None
