import pyrealsense2 as rs
import numpy as np
import cv2
import os
import queue
import threading
import time


class RealSenseCamera:

    def __init__(self):
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.profile = None

        self._start_pipeline_with_fallbacks()

        self.align = rs.align(rs.stream.color)
        self.pc = rs.pointcloud()

        self.writer = None
        self.recording = False
        self.frame_count = 0
        self.video_fps = 10
        self.running = False
        self.capture_thread = None
        self.process_thread = None
        self.frame_queue = queue.Queue(maxsize=max(1, int(os.getenv("GMA_RS_QUEUE_SIZE", "2"))))
        self.queue_drops = 0
        self.capture_frames = 0
        self.processed_frames = 0
        self.last_error = None
        self._capture_t0 = 0.0
        self._last_fps_log = 0.0

        # Heavy disk writes are decimated to keep real-time video recording stable on Raspberry Pi.
        self.save_rgb_depth_every = max(1, int(os.getenv("GMA_SAVE_RGB_DEPTH_EVERY", "5")))
        self.save_pointcloud_every = max(1, int(os.getenv("GMA_SAVE_POINTCLOUD_EVERY", "20")))

    def _start_pipeline_with_fallbacks(self):
        # Prefer low FPS on Raspberry Pi; fall back to commonly supported modes.
        attempts = [
            (640, 480, 10),
            (640, 480, 9),
            (640, 480, 8),
            (640, 480, 15),
            (640, 480, 30),
            (424, 240, 10),
            (424, 240, 9),
            (424, 240, 8),
            (424, 240, 15),
            (424, 240, 30),
        ]

        last_error = None
        for w, h, fps in attempts:
            config = rs.config()
            config.enable_stream(rs.stream.depth, w, h, rs.format.z16, fps)
            config.enable_stream(rs.stream.color, w, h, rs.format.bgr8, fps)
            try:
                self.profile = self.pipeline.start(config)
                self.width = w
                self.height = h
                self.sensor_fps = fps
                return
            except RuntimeError as err:
                last_error = err

        raise RuntimeError(f"RealSense pipeline start failed for all profiles: {last_error}")

    def setup_folders(self, session_path):
        self.base = os.path.join(session_path, "realsense")

        self.rgb_dir = os.path.join(self.base, "rgb")
        self.depth_dir = os.path.join(self.base, "depth")
        self.ply_dir = os.path.join(self.base, "pointcloud")

        os.makedirs(self.rgb_dir, exist_ok=True)
        os.makedirs(self.depth_dir, exist_ok=True)
        os.makedirs(self.ply_dir, exist_ok=True)

    def start(self, video_path, video_fps=10):
        # AVI+MJPG is more reliable on Raspberry Pi OpenCV builds than MP4 containers.
        base, _ = os.path.splitext(video_path)
        out_path = f"{base}.avi"
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")

        # Use actual negotiated stream FPS.
        self.video_fps = max(1, int(getattr(self, "sensor_fps", video_fps)))
        self.writer = cv2.VideoWriter(out_path, fourcc, self.video_fps, (self.width, self.height))
        if not self.writer.isOpened():
            raise RuntimeError(f"Failed to open RealSense video writer: {out_path}")
        self.recording = True
        self.path = out_path

        self.running = True
        self.frame_count = 0
        self.capture_frames = 0
        self.processed_frames = 0
        self.queue_drops = 0
        self.last_error = None
        self._capture_t0 = time.monotonic()
        self._last_fps_log = self._capture_t0

        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.process_thread = threading.Thread(target=self._process_loop, daemon=True)
        self.capture_thread.start()
        self.process_thread.start()

    def _capture_loop(self):
        while self.running:
            try:
                frames = self.pipeline.wait_for_frames(timeout_ms=1000)
                aligned = self.align.process(frames)

                depth_frame = aligned.get_depth_frame()
                color_frame = aligned.get_color_frame()

                if not depth_frame or not color_frame:
                    continue

                # Keep frame handles alive after this scope so worker can process them.
                depth_frame.keep()
                color_frame.keep()

                timestamp_ms = float(color_frame.get_timestamp())
                frame_number = int(color_frame.get_frame_number())

                try:
                    while not self.frame_queue.empty():
                        try:
                            self.frame_queue.get_nowait()
                        except queue.Empty:
                            break
                    self.frame_queue.put_nowait((color_frame, depth_frame, timestamp_ms, frame_number))
                except queue.Full:
                    self.queue_drops += 1

                self.capture_frames += 1
                self._log_capture_fps()
            except Exception as err:
                self.last_error = err
                self.running = False
                break

    def _log_capture_fps(self):
        now = time.monotonic()
        if now - self._last_fps_log < 2.0:
            return

        elapsed = max(1e-6, now - self._capture_t0)
        fps = self.capture_frames / elapsed
        print(
            f"RealSense capture fps={fps:.2f} expected={self.sensor_fps} "
            f"queue={self.frame_queue.qsize()}/{self.frame_queue.maxsize} dropped={self.queue_drops}"
        )
        self._last_fps_log = now

    def _process_loop(self):
        while self.running or not self.frame_queue.empty():
            try:
                color_frame, depth_frame, timestamp_ms, frame_number = self.frame_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            try:
                color = np.asanyarray(color_frame.get_data())
                depth = np.asanyarray(depth_frame.get_data())

                # Save 2D reference video in worker thread.
                if self.recording and self.writer is not None:
                    self.writer.write(color)

                # Depth is saved every frame so playback never reuses stale maps.
                np.save(os.path.join(self.depth_dir, f"{frame_number}.npy"), depth)

                if self.frame_count % self.save_rgb_depth_every == 0:
                    cv2.imwrite(os.path.join(self.rgb_dir, f"{frame_number}.png"), color)

                if self.frame_count % self.save_pointcloud_every == 0:
                    points = self.pc.calculate(depth_frame)
                    self.pc.map_to(color_frame)

                    vertices = np.asanyarray(points.get_vertices()).view(np.float32).reshape(-1, 3)
                    colors = color.reshape(-1, 3) / 255.0
                    np.savez_compressed(
                        os.path.join(self.ply_dir, f"{frame_number}.npz"),
                        xyz=vertices,
                        rgb=colors,
                        timestamp_ms=timestamp_ms,
                        frame_number=frame_number,
                    )

                self.frame_count += 1
                self.processed_frames += 1
            except Exception as err:
                self.last_error = err
                self.running = False
                break

    def capture(self):
        # Capture is fully handled by internal capture/worker threads.
        return

    def stop(self):
        self.running = False
        if self.capture_thread is not None and self.capture_thread.is_alive():
            self.capture_thread.join()
        if self.process_thread is not None and self.process_thread.is_alive():
            self.process_thread.join()
        self.capture_thread = None
        self.process_thread = None

        if self.writer is not None:
            self.writer.release()
            self.writer = None
        try:
            self.pipeline.stop()
        except Exception:
            pass
