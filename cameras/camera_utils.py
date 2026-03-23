import cv2

def find_working_cameras(max_index=10):
    working = []

    for i in range(max_index):
        cap = cv2.VideoCapture(i)

        if not cap.isOpened():
            cap.release()
            continue

        ret, frame = cap.read()

        # 🔴 Strict validation
        if ret and frame is not None:
            h, w = frame.shape[:2]

            # Ignore tiny / invalid streams (RealSense junk nodes)
            if w >= 1280 and h >= 720:
                working.append(i)

        cap.release()

    return working
