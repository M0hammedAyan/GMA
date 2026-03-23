import cv2

cap = cv2.VideoCapture(0)

for w, h in [(640,480),(1280,720),(1920,1080)]:
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

    real_w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    real_h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    print(f"Requested {w}x{h} -> Got {real_w}x{real_h}")

cap.release()
