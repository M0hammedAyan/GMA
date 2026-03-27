import pyrealsense2 as rs
import numpy as np
import cv2
import os


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
        self.video_fps = video_fps
        self.writer = cv2.VideoWriter(out_path, fourcc, self.video_fps, (self.width, self.height))
        if not self.writer.isOpened():
            raise RuntimeError(f"Failed to open RealSense video writer: {out_path}")
        self.recording = True
        self.path = out_path

    def capture(self):
        frames = self.pipeline.wait_for_frames(timeout_ms=1000)
        aligned = self.align.process(frames)

        depth_frame = aligned.get_depth_frame()
        color_frame = aligned.get_color_frame()

        if not depth_frame or not color_frame:
            return

        color = np.asanyarray(color_frame.get_data())
        depth = np.asanyarray(depth_frame.get_data())

        # Save 2D reference video
        if self.recording:
            self.writer.write(color)

        if self.frame_count % self.save_rgb_depth_every == 0:
            # Save RGB + Depth (3D data sources)
            cv2.imwrite(os.path.join(self.rgb_dir, f"{self.frame_count}.png"), color)
            np.save(os.path.join(self.depth_dir, f"{self.frame_count}.npy"), depth)

        if self.frame_count % self.save_pointcloud_every == 0:
            # Point cloud export is the most expensive operation, so save it less frequently.
            points = self.pc.calculate(depth_frame)
            self.pc.map_to(color_frame)

            vertices = np.asanyarray(points.get_vertices()).view(np.float32).reshape(-1, 3)
            colors = color.reshape(-1, 3) / 255.0
            np.savez_compressed(
                os.path.join(self.ply_dir, f"{self.frame_count}.npz"),
                xyz=vertices,
                rgb=colors,
            )

        self.frame_count += 1

    def stop(self):
        if self.writer is not None:
            self.writer.release()
            self.writer = None
        try:
            self.pipeline.stop()
        except Exception:
            pass
