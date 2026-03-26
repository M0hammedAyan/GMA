import glob
import os
import re
import subprocess

import cv2
import pyrealsense2 as rs


def _video_nodes():
    nodes = []
    for path in sorted(glob.glob("/dev/video*")):
        name = os.path.basename(path)
        m = re.match(r"video(\d+)$", name)
        if m:
            nodes.append((int(m.group(1)), path))
    return nodes


def _v4l2_card_name(node_path):
    try:
        result = subprocess.run(
            ["v4l2-ctl", "-D", "-d", node_path],
            capture_output=True,
            text=True,
            timeout=1.5,
            check=False,
        )
    except Exception:
        return ""

    if result.returncode != 0:
        return ""

    for line in result.stdout.splitlines():
        if line.strip().startswith("Card type"):
            return line.split(":", 1)[-1].strip().lower()
    return ""


def _looks_like_realsense(node_path):
    card = _v4l2_card_name(node_path)
    return "realsense" in card or "intel" in card


def find_webcam():
    for _, node_path in _video_nodes():
        if _looks_like_realsense(node_path):
            continue

        cap = cv2.VideoCapture(node_path, cv2.CAP_V4L2)
        if not cap.isOpened():
            cap.release()
            continue

        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        ret, frame = cap.read()
        cap.release()

        if not ret or frame is None:
            continue

        h, w = frame.shape[:2]
        if w >= 320 and h >= 240:
            return node_path

    return None


def check_realsense():
    ctx = rs.context()
    return len(ctx.query_devices()) > 0
