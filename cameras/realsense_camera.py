import pyrealsense2 as rs
import numpy as np
import cv2
import time


class RealSenseCamera:

    def __init__(self):
        self.pipeline = rs.pipeline()
        config = rs.config()

        # 🔥 Lower resolution for stability
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 15)

        self.pipeline.start(config)

        self.recording = False
        self.writer = None

    def start_recording(self, path):
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")

        # 🔥 Match realistic FPS
        self.writer = cv2.VideoWriter(path, fourcc, 10, (640, 480))

        self.recording = True

    def capture(self):

        if not self.recording:
            return

        frames = self.pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()

        if not color_frame:
            return

        frame = np.asanyarray(color_frame.get_data())
        self.writer.write(frame)

    def stop_recording(self):
        self.recording = False
        if self.writer:
            self.writer.release()

    def release(self):
        self.pipeline.stop()
