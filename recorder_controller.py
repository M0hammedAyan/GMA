import os
import threading
from datetime import datetime

from Recordings.Cameras.Cam_Sim1 import SimCamera1
from Recordings.Cameras.Cam_Sim2 import SimCamera2


class RecorderController:

    def __init__(self):
        self.cam1 = SimCamera1()
        self.cam2 = SimCamera2()
        self.start_event = threading.Event()
        self.stop_event = threading.Event()

    def create_session_folder(self):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder = f"Recordings/session_{ts}"
        os.makedirs(folder, exist_ok=True)
        return folder

    def start_recording(self):
        self.stop_event.clear()
        folder = self.create_session_folder()
        cam1_path = f"{folder}/cam1.mp4"
        cam2_path = f"{folder}/cam2.mp4"
        t1 = threading.Thread(target=self.record_cam1, args=(cam1_path,))
        t2 = threading.Thread(target=self.record_cam2, args=(cam2_path,))
        t1.start()
        t2.start()
        self.start_event.set()

    def record_cam1(self, path):
        self.start_event.wait()
        self.cam1.start_recording(path)
        while not self.stop_event.is_set():
            self.cam1.capture()
        self.cam1.stop_recording()

    def record_cam2(self, path):
        self.start_event.wait()
        self.cam2.start_recording(path)
        while not self.stop_event.is_set():
            self.cam2.capture()
        self.cam2.stop_recording()

    def stop_recording(self):
        self.stop_event.set()