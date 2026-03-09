import cv2
import os
import threading
from datetime import datetime


class RecorderController:

    def __init__(self):

        # CHANGE CAMERA INDEXES HERE
        self.CAM1_INDEX = 0
        self.CAM2_INDEX = 1

        self.recording = False
        self.cam1 = None
        self.cam2 = None
        self.out1 = None
        self.out2 = None
        self.thread = None
        self.folder = ""

    def start_recording(self):

        if self.recording:
            print("Recording already running")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.folder = os.path.join("recordings", f"session_{timestamp}")
        os.makedirs(self.folder, exist_ok=True)

        self.cam1 = cv2.VideoCapture(self.CAM1_INDEX)
        self.cam2 = cv2.VideoCapture(self.CAM2_INDEX)

        if not self.cam1.isOpened() or not self.cam2.isOpened():
            print("Error: Could not open cameras")
            return

        ret1, frame1 = self.cam1.read()
        ret2, frame2 = self.cam2.read()

        if not ret1 or not ret2:
            print("Error reading frames")
            return

        h1, w1 = frame1.shape[:2]
        h2, w2 = frame2.shape[:2]

        fourcc = cv2.VideoWriter_fourcc(*'MJPG')

        self.out1 = cv2.VideoWriter(
            os.path.join(self.folder, f"cam1_idx{self.CAM1_INDEX}.avi"),
            fourcc,
            30,
            (w1, h1)
        )

        self.out2 = cv2.VideoWriter(
            os.path.join(self.folder, f"cam2_idx{self.CAM2_INDEX}.avi"),
            fourcc,
            30,
            (w2, h2)
        )

        self.recording = True
        self.thread = threading.Thread(target=self.record_loop)
        self.thread.start()

        print("Recording started")

    def record_loop(self):

        while self.recording:

            ret1, frame1 = self.cam1.read()
            ret2, frame2 = self.cam2.read()

            if ret1:
                self.out1.write(frame1)

            if ret2:
                self.out2.write(frame2)

    def stop_recording(self):

        if not self.recording:
            print("Recording not running")
            return

        self.recording = False

        if self.thread:
            self.thread.join()

        self.cam1.release()
        self.cam2.release()
        self.out1.release()
        self.out2.release()

        cv2.destroyAllWindows()

        print("Recording saved in:", self.folder)