import cv2

class SimCamera2:

    def __init__(self):
        self.cap = cv2.VideoCapture(1)
        self.recording = False

    def start_recording(self, path):

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # type: ignore
        self.writer = cv2.VideoWriter(path, fourcc, 60, (1280,720))

        self.recording = True

    def capture(self):

        if self.recording:
            ret, frame = self.cap.read()
            if ret:
                self.writer.write(frame)

    def stop_recording(self):

        self.recording = False
        self.writer.release()
        self.cap.release()