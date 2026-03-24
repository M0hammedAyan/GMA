import cv2


class Camera:

    def __init__(self, index):
        self.cap = cv2.VideoCapture(index)

        if not self.cap.isOpened():
            raise Exception(f"Failed to open webcam at index {index}")

        self.recording = False
        self.writer = None

    def start_recording(self, path):
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.writer = cv2.VideoWriter(path, fourcc, 30, (width, height))
        self.recording = True

    def capture(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        if self.recording:
            self.writer.write(frame)

    def stop_recording(self):
        self.recording = False
        if self.writer:
            self.writer.release()

    def release(self):
        self.cap.release()
