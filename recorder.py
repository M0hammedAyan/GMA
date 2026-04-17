# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportMissingParameterType=false, reportGeneralTypeIssues=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

import os
import shutil
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
        self.capture_fps = max(1, int(os.getenv("GMA_CAPTURE_FPS", "30")))
        self.min_free_mb = max(1, int(os.getenv("GMA_MIN_FREE_MB", "512")))

    def _ensure_free_space(self):
        # Guard native writers from ENOSPC-triggered aborts.
        target = self.output_root if os.path.exists(self.output_root) else "."
        free_mb = shutil.disk_usage(target).free / (1024 * 1024)
        if free_mb < float(self.min_free_mb):
            raise RuntimeError(
                f"Insufficient disk space for recording: {free_mb:.1f} MB free, "
                f"requires at least {self.min_free_mb} MB"
            )

    def start(self):
        if self.running:
            return

        self.last_error = None
        self._ensure_free_space()

        webcam_device = find_webcam()
        if webcam_device is None:
            raise Exception("No webcam detected")

        if not check_realsense():
            raise Exception("RealSense not detected")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_path = os.path.join(self.output_root, f"session_{timestamp}")

        try:
            self.realsense = RealSenseCamera()
            self.webcam = Webcam(webcam_device)

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

        self.webcam_thread = threading.Thread(target=self._webcam_loop, daemon=True)
        self.webcam_thread.start()

        print("Recording started")

    def _webcam_loop(self):
        interval = 1.0 / float(self.capture_fps)
        next_time = time.monotonic()
        last_space_check = 0.0

        while self.running:
            if self.realsense is not None and self.realsense.last_error is not None:
                self.last_error = self.realsense.last_error
                self.running = False
                break

            if self.webcam is not None and self.webcam.last_error is not None:
                self.last_error = self.webcam.last_error
                self.running = False
                break

            now = time.monotonic()
            if now - last_space_check >= 1.0:
                try:
                    self._ensure_free_space()
                except Exception as err:
                    self.last_error = err
                    self.running = False
                    break
                last_space_check = now

            if now < next_time:
                time.sleep(next_time - now)
                continue

            try:
                if self.webcam is not None:
                    self.webcam.capture()
            except Exception as err:
                self.last_error = err
                self.running = False
                break

            next_time = max(next_time + interval, time.monotonic())

    def stop(self):
        self.running = False

        if self.webcam_thread and self.webcam_thread.is_alive():
            self.webcam_thread.join(timeout=2.0)
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

    def get_preview_frames(self):
        rs_color = None
        rs_depth = None
        webcam = None

        if self.realsense is not None:
            rs_color, rs_depth = self.realsense.get_latest_preview_frames()

        if self.webcam is not None:
            webcam = self.webcam.get_latest_frame()

        return {
            "realsense_color": rs_color,
            "realsense_depth": rs_depth,
            "webcam": webcam,
        }
