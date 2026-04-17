import cv2
import os
import queue
import threading


class Webcam:

    def __init__(self, device):
        self.device = device
        self.cap = cv2.VideoCapture(device, cv2.CAP_V4L2)

        if not self.cap.isOpened():
            raise Exception(f"Webcam not found: {device}")

        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        self.writer = None
        self.recording = False
        self._frame_lock = threading.Lock()
        self._latest_frame = None
        self._writer_queue = queue.Queue(maxsize=180)
        self._writer_stop = threading.Event()
        self._writer_thread = None
        self.last_error = None

    def start(self, path, video_fps=10):
        # AVI+MJPG is more reliable on Raspberry Pi OpenCV builds than MP4 containers.
        base, _ = os.path.splitext(path)
        out_path = f"{base}.avi"
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")

        w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if w <= 0 or h <= 0:
            w, h = 640, 480

        self.writer = cv2.VideoWriter(out_path, fourcc, video_fps, (w, h))
        if not self.writer.isOpened():
            raise RuntimeError(f"Failed to open webcam writer: {out_path}")
        self.last_error = None
        while not self._writer_queue.empty():
            try:
                self._writer_queue.get_nowait()
            except queue.Empty:
                break
        self._writer_stop.clear()
        self._writer_thread = threading.Thread(target=self._writer_loop, daemon=True)
        self._writer_thread.start()
        self.recording = True
        self.path = out_path

    def _writer_loop(self):
        while not self._writer_stop.is_set() or not self._writer_queue.empty():
            try:
                frame = self._writer_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            try:
                if self.writer is not None:
                    self.writer.write(frame)
            except Exception as err:
                self.last_error = err
                self.recording = False
                self._writer_stop.set()
                break

    def capture(self):
        ret, frame = self.cap.read()
        if not ret or frame is None or frame.size == 0:
            return

        frame_copy = frame.copy()
        with self._frame_lock:
            self._latest_frame = frame_copy

        if self.recording and self.writer is not None:
            try:
                self._writer_queue.put_nowait(frame_copy)
            except queue.Full:
                try:
                    self._writer_queue.get_nowait()
                except queue.Empty:
                    pass
                try:
                    self._writer_queue.put_nowait(frame_copy)
                except queue.Full:
                    pass

    def get_latest_frame(self):
        with self._frame_lock:
            if self._latest_frame is None:
                return None
            return self._latest_frame.copy()

    def stop(self):
        self.recording = False
        self._writer_stop.set()
        if self._writer_thread is not None and self._writer_thread.is_alive():
            self._writer_thread.join(timeout=2.0)
        self._writer_thread = None

        if self.writer is not None:
            self.writer.release()
            self.writer = None

        while not self._writer_queue.empty():
            try:
                self._writer_queue.get_nowait()
            except queue.Empty:
                break

        with self._frame_lock:
            self._latest_frame = None
        self.cap.release()
