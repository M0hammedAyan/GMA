import cv2
import pyrealsense2 as rs


def find_webcam(max_index=10):
    for i in range(max_index):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret:
                return i
    return None


def check_realsense():
    ctx = rs.context()
    devices = ctx.query_devices()
    return len(devices) > 0
