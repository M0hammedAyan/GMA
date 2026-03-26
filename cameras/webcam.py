import cv2


class Webcam:

    def __init__(self, device):
        self.device = device
        self.cap = cv2.VideoCapture(device, cv2.CAP_V4L2)

        if not self.cap.isOpened():
            raise Exception(f"Webcam not found: {device}")

        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        self.writer = None
        self.recording = False

    def start(self, path):
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")

        w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if w <= 0 or h <= 0:
            w, h = 640, 480

        self.writer = cv2.VideoWriter(path, fourcc, 10, (w, h))
        if not self.writer.isOpened():
            raise RuntimeError(f"Failed to open webcam writer: {path}")
        self.recording = True

    def capture(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        if self.recording and self.writer is not None:
            self.writer.write(frame)

    def stop(self):
        if self.writer is not None:
            self.writer.release()
            self.writer = None
        self.cap.release()
