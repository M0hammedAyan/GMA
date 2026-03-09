import cv2

print("Scanning camera indexes...\n")

for i in range(8):

    cap = cv2.VideoCapture(i)

    if not cap.isOpened():
        print(f"Index {i}: cannot open")
        continue

    ret, frame = cap.read()

    if ret:
        h, w = frame.shape[:2]
        print(f"Index {i}: WORKING ({w}x{h})")

        cv2.imshow(f"Camera {i}", frame)
        cv2.waitKey(1500)

    else:
        print(f"Index {i}: opened but no frames")

    cap.release()

cv2.destroyAllWindows()