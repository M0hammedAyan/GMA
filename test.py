import cv2

print("Scanning cameras...\n")

working = []

for i in range(10):

    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)

    if cap.isOpened():
        ret, frame = cap.read()

        if ret:
            print(f"Camera {i} is working")
            working.append(i)
        else:
            print(f"Camera {i} opened but no frame")

    cap.release()

print("\nWorking camera indexes:", working)