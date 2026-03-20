import cv2
import time


class Camera:
    def __init__(self, index):
        self.index = index
        self.cap = cv2.VideoCapture(index)

        if not self.cap.isOpened():
            raise RuntimeError(f"Camera {index} could not be opened")

        # Set resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.recording = False
        self.writer = None

        self.last_time = None

    def start_recording(self, path):
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")

        # 🔥 Start with safe FPS
        self.writer = cv2.VideoWriter(path, fourcc, 10, (self.width, self.height))

        self.recording = True
        self.last_time = time.time()

    def capture(self):
        if not self.recording:
            return

        ret, frame = self.cap.read()

        if not ret:
            print(f"[WARNING] Camera {self.index}: Failed to read frame")
            return

        # Write frame
        self.writer.write(frame)

    def stop_recording(self):
        self.recording = False
        if self.writer:
            self.writer.release()

    def release(self):
        if self.cap:
            self.cap.release()
