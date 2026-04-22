import cv2
import os
import threading
import time
import numpy as np


class Webcam:

    def __init__(self, device):
        self.device = device
        self.cap = cv2.VideoCapture(device, cv2.CAP_V4L2)

        if not self.cap.isOpened():
            raise Exception(f"Webcam not found: {device}")

        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        # Set highest resolution webcam supports
        resolutions = [(1920, 1080), (1280, 720), (1024, 768), (640, 480)]
        for w, h in resolutions:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
            actual_w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            if actual_w == w and actual_h == h:
                print(f"Webcam resolution set to {w}x{h}")
                break

        self.writer = None
        self.recording = False
        self._frame_lock = threading.Lock()
        self._latest_frame = None
        self._latest_ts = 0.0
        self._last_output_frame = None
        self._stop_event = threading.Event()
        self._capture_thread = None
        self._record_thread = None
        self.last_error = None
        self.actual_fps = 30.0
        self._record_started_at = 0.0
        self._record_stop_at = None
        self._record_gate = threading.Event()
        self._writer_lock = threading.Lock()

    def start(self, path, video_fps=10, started_at=None):
        # AVI+MJPG is more reliable on Raspberry Pi OpenCV builds than MP4 containers.
        base, _ = os.path.splitext(path)
        out_path = f"{base}.avi"
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")

        w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if w <= 0 or h <= 0:
            w, h = 640, 480

        write_fps = max(1, int(round(float(video_fps))))

        self.writer = cv2.VideoWriter(out_path, fourcc, float(write_fps), (w, h))
        if not self.writer.isOpened():
            raise RuntimeError(f"Failed to open webcam writer: {out_path}")
        self.last_error = None
        self._stop_event.clear()
        self._record_gate.clear()
        self._last_output_frame = None
        self._blank_frame = np.zeros((h, w, 3), dtype=np.uint8)
        self._record_started_at = time.monotonic() if started_at is None else float(started_at)
        if started_at is not None:
            self._record_gate.set()
        self._record_stop_at = None
        self._capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._record_thread = threading.Thread(target=self._record_loop, args=(float(write_fps),), daemon=True)
        self._capture_thread.start()
        self._record_thread.start()
        self.recording = True
        self.path = out_path
        self.actual_fps = float(write_fps)
        print(f"Webcam stream configured: {w}x{h}@{self.actual_fps:.2f}")
        return write_fps

    def _capture_loop(self):
        while not self._stop_event.is_set():
            try:
                ret, frame = self.cap.read()
            except Exception as err:
                self.last_error = err
                self.recording = False
                self._stop_event.set()
                break

            if not ret or frame is None or frame.size == 0:
                continue

            with self._frame_lock:
                self._latest_frame = frame.copy()
                self._latest_ts = time.time()

    def _record_loop(self, target_fps):
        target_fps = float(max(1.0, target_fps))
        written_count = 0

        while True:
            if not self._record_gate.is_set():
                time.sleep(0.002)
                continue

            if self._stop_event.is_set():
                stop_at = self._record_stop_at if self._record_stop_at is not None else time.monotonic()
                elapsed = max(0.0, stop_at - self._record_started_at)
                target_frames = int(round(elapsed * target_fps))
                due_frames = target_frames - written_count
                if due_frames <= 0:
                    break
            else:
                elapsed = max(0.0, time.monotonic() - self._record_started_at)
                target_frames = int(elapsed * target_fps)
                due_frames = target_frames - written_count
                if due_frames <= 0:
                    time.sleep(0.002)
                    continue

            with self._frame_lock:
                if self._latest_frame is not None:
                    frame = self._latest_frame.copy()
                    self._last_output_frame = frame.copy()
                elif self._last_output_frame is not None:
                    frame = self._last_output_frame.copy()
                else:
                    frame = None

            if frame is None:
                frame = self._blank_frame

            if frame is not None and self.writer is not None:
                with self._writer_lock:
                    for _ in range(max(1, due_frames)):
                        try:
                            if self.writer is None:
                                return
                            self.writer.write(frame)
                        except Exception as err:
                            self.last_error = err
                            self.recording = False
                            self._stop_event.set()
                            return
                        written_count += 1

    def capture(self):
        return

    def get_latest_frame(self):
        with self._frame_lock:
            if self._latest_frame is None:
                return None
            return self._latest_frame.copy()

    def set_recording_start_time(self, started_at):
        self._record_started_at = float(started_at)
        self._record_gate.set()

    def set_recording_stop_time(self, stop_at):
        self._record_stop_at = float(stop_at)

    def request_stop(self):
        self._stop_event.set()

    def stop(self):
        self.recording = False
        if self._record_stop_at is None:
            self._record_stop_at = time.monotonic()
        self._stop_event.set()
        if self._capture_thread is not None and self._capture_thread.is_alive():
            self._capture_thread.join()
        if self._record_thread is not None and self._record_thread.is_alive():
            self._record_thread.join()
        self._capture_thread = None
        self._record_thread = None

        with self._writer_lock:
            if self.writer is not None:
                self.writer.release()
                self.writer = None

        with self._frame_lock:
            self._latest_frame = None
            self._latest_ts = 0.0
            self._last_output_frame = None
        self.cap.release()
