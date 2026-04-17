import glob
import os
import re
import subprocess
from typing import List, Optional, Tuple

import cv2
try:
    import pyrealsense2 as rs
except ImportError:
    rs = None


def _video_nodes() -> List[Tuple[int, str]]:
    nodes: List[Tuple[int, str]] = []
    for path in sorted(glob.glob("/dev/video*")):
        name = os.path.basename(path)
        m = re.match(r"video(\d+)$", name)
        if m:
            nodes.append((int(m.group(1)), path))
    return nodes


def _v4l2_card_name(node_path: str) -> str:
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


def _v4l2_has_capture_capability(node_path: str) -> bool:
    try:
        result = subprocess.run(
            ["v4l2-ctl", "-D", "-d", node_path],
            capture_output=True,
            text=True,
            timeout=1.5,
            check=False,
        )
    except Exception:
        return False

    if result.returncode != 0:
        return False

    info = result.stdout.lower()
    return "video capture" in info


def _looks_like_realsense(node_path: str) -> bool:
    card = _v4l2_card_name(node_path)
    return "realsense" in card or "intel" in card


def _list_candidate_nodes_from_v4l2() -> List[str]:
    try:
        result = subprocess.run(
            ["v4l2-ctl", "--list-devices"],
            capture_output=True,
            text=True,
            timeout=2.0,
            check=False,
        )
    except Exception:
        return []

    if result.returncode != 0:
        return []

    nodes: List[str] = []
    current_device_name = ""

    for raw_line in result.stdout.splitlines():
        line = raw_line.rstrip()
        if not line:
            current_device_name = ""
            continue

        if not line.startswith("\t"):
            current_device_name = line.lower().strip()
            continue

        node = line.strip()
        if not node.startswith("/dev/video"):
            continue

        # Skip known non-webcam groups.
        if (
            "realsense" in current_device_name
            or "intel" in current_device_name
            or "pisp" in current_device_name
            or "rpi-hevc" in current_device_name
        ):
            continue

        nodes.append(node)

    return nodes


def _openable_webcam(node_path: str) -> bool:
    if _looks_like_realsense(node_path):
        return False

    if not _v4l2_has_capture_capability(node_path):
        return False

    cap = cv2.VideoCapture(node_path, cv2.CAP_V4L2)
    if not cap.isOpened():
        cap.release()
        return False

    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        return False

    h, w = frame.shape[:2]
    return w >= 320 and h >= 240


def find_webcam() -> Optional[str]:
    # Prefer device groups from v4l2-ctl to avoid probing non-capture nodes.
    for node_path in _list_candidate_nodes_from_v4l2():
        if _openable_webcam(node_path):
            return node_path

    # Fallback if v4l2-ctl output is unavailable or incomplete.
    for _, node_path in _video_nodes():
        if _openable_webcam(node_path):
            return node_path

    return None


def check_realsense():
    if rs is None:
        return False
    ctx = rs.context()
    return len(ctx.query_devices()) > 0
