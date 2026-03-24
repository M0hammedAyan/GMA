import pyrealsense2 as rs
import numpy as np
import cv2
import os


class RealSenseCamera:

    def __init__(self):
        self.pipeline = rs.pipeline()
        config = rs.config()

        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

        self.pipeline.start(config)

        self.align = rs.align(rs.stream.color)
        self.pc = rs.pointcloud()

        self.recording = False
        self.writer = None

        self.frame_count = 0
        self.output_folder = None

    def set_output_folder(self, folder):
        self.output_folder = os.path.join(folder, "ply_frames")
        os.makedirs(self.output_folder, exist_ok=True)

    def start_recording(self, path):
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.writer = cv2.VideoWriter(path, fourcc, 30, (640, 480))
        self.recording = True

    def capture(self):
        frames = self.pipeline.wait_for_frames()
        aligned = self.align.process(frames)

        depth_frame = aligned.get_depth_frame()
        color_frame = aligned.get_color_frame()

        if not depth_frame or not color_frame:
            return

        color_image = np.asanyarray(color_frame.get_data())

        # Save RGB video
        if self.recording:
            self.writer.write(color_image)

        # Generate point cloud
        points = self.pc.calculate(depth_frame)
        self.pc.map_to(color_frame)

        # Save every 30 frames
        if self.output_folder and self.frame_count % 30 == 0:
            filename = os.path.join(self.output_folder, f"frame_{self.frame_count}.ply")
            points.export_to_ply(filename, color_frame)

        self.frame_count += 1

    def stop_recording(self):
        self.recording = False
        if self.writer:
            self.writer.release()

    def release(self):
        self.pipeline.stop()
