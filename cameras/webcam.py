import cv2
import os
import threading
import time


class Webcam:

    def __init__(self, device):
        self.device = device
        self.cap = cv2.VideoCapture(device, cv2.CAP_V4L2)

        if not self.cap.isOpened():
            raise Exception(f"Webcam not found: {device}")

        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        # Use Pi-safe defaults first; allow overrides through env vars.
        env_w = int(os.getenv("GMA_WEBCAM_WIDTH", "640"))
        env_h = int(os.getenv("GMA_WEBCAM_HEIGHT", "480"))
        resolutions = [
            (env_w, env_h),
            (640, 480),
            (960, 540),
            (1280, 720),
            (1920, 1080),
        ]
        seen = set()
        resolutions = [r for r in resolutions if not (r in seen or seen.add(r))]
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
        self._stop_event = threading.Event()
        self._capture_thread = None
        self._record_thread = None
        self.last_error = None
        self.actual_fps = 30.0
        self._record_started_at = 0.0
        self._record_stop_at = None
        self._record_gate = threading.Event()
        self._writer_lock = threading.Lock()
        self._captured_frames = 0
        self._written_frames = 0
        self._dropped_early = 0
        self._dropped_late = 0
        self._dropped_queue = 0

    def start(self, path, video_fps=10, started_at=None):
        # AVI+MJPG is more reliable on Raspberry Pi OpenCV builds than MP4 containers.
        base, _ = os.path.splitext(path)
        out_path = f"{base}.avi"

        write_fps = float(max(1, int(round(float(video_fps)))))

        self.writer = None
        self.last_error = None
        self._stop_event.clear()
        self._record_gate.clear()
        self._captured_frames = 0
        self._written_frames = 0
        self._record_started_at = time.monotonic() if started_at is None else float(started_at)
        if started_at is not None:
            self._record_gate.set()
        self._record_stop_at = None
        self._capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._record_thread = threading.Thread(target=self._record_loop, args=(out_path, write_fps), daemon=True)
        self._capture_thread.start()
        self._record_thread.start()
        self.recording = True
        self.path = out_path
        self.actual_fps = write_fps
        print(f"Webcam recording started: target_fps={self.actual_fps:.2f} output={out_path}")
        return int(round(write_fps))

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

            capture_ts = time.monotonic()
            self._captured_frames += 1

            with self._frame_lock:
                self._latest_frame = frame.copy()
                self._latest_ts = capture_ts

    def _record_loop(self, out_path, target_fps):
        write_fps = float(max(1.0, target_fps))
        frame_interval = 1.0 / write_fps
        start_wall = 0.0
        next_frame_time = 0.0
        expected_frames = 0

        def _open_writer(sample_frame):
            h, w = sample_frame.shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*"MJPG")
            writer = cv2.VideoWriter(out_path, fourcc, write_fps, (w, h))
            if not writer.isOpened():
                raise RuntimeError(f"Failed to open webcam writer: {out_path}")
            return writer

        try:
            while True:
                if self._stop_event.is_set() and not self._record_gate.is_set():
                    break

                if not self._record_gate.is_set():
                    time.sleep(0.002)
                    continue

                if start_wall <= 0.0:
                    start_wall = self._record_started_at if self._record_started_at > 0.0 else time.monotonic()
                    next_frame_time = start_wall

                if self.writer is None:
                    with self._frame_lock:
                        frame = None if self._latest_frame is None else self._latest_frame.copy()
                    if frame is None:
                        if self._stop_event.is_set():
                            break
                        time.sleep(0.001)
                        continue
                    self.writer = _open_writer(frame)
                    self.actual_fps = write_fps
                    print(f"Webcam writer opened fps={write_fps:.2f} size={frame.shape[1]}x{frame.shape[0]}")

                now = time.monotonic()
                if self._record_stop_at is not None and now >= self._record_stop_at:
                    self._stop_event.set()
                    break
                if now < next_frame_time:
                    time.sleep(min(0.01, next_frame_time - now))
                    continue

                if now - next_frame_time > frame_interval:
                    self._dropped_late += 1
                    next_frame_time = now

                expected_frames += 1
                with self._frame_lock:
                    frame = None if self._latest_frame is None else self._latest_frame.copy()

                if frame is None:
                    next_frame_time += frame_interval
                    if self._stop_event.is_set():
                        break
                    continue

                with self._writer_lock:
                    if self.writer is None:
                        return
                    self.writer.write(frame)

                self._written_frames += 1
                next_frame_time += frame_interval
        except Exception as err:
            self.last_error = err
            self.recording = False
            self._stop_event.set()
        finally:
            duration_real = 0.0 if start_wall is None else max(0.0, time.monotonic() - start_wall)
            duration_video = 0.0 if write_fps <= 0 else (self._written_frames / write_fps)
            effective_fps = 0.0 if duration_real <= 0 else (float(self._written_frames) / duration_real)
            print(
                "Webcam timing stats: "
                f"captured={self._captured_frames} written={self._written_frames} "
                f"expected={expected_frames} "
                f"writer_fps={write_fps:.2f} effective_fps={effective_fps:.2f} "
                f"real_s={duration_real:.2f} video_s={duration_video:.2f}"
            )

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
        try:
            self.cap.release()
        except Exception:
            pass
        if self._capture_thread is not None and self._capture_thread.is_alive():
            self._capture_thread.join(timeout=2.0)
        if self._record_thread is not None and self._record_thread.is_alive():
            self._record_thread.join(timeout=3.0)
        self._capture_thread = None
        self._record_thread = None

        with self._writer_lock:
            if self.writer is not None:
                self.writer.release()
                self.writer = None

        with self._frame_lock:
            self._latest_frame = None
            self._latest_ts = 0.0
