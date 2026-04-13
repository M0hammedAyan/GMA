import os
import queue
import threading
import time
import argparse
from datetime import datetime
from typing import Any

import cv2
import numpy as np
import pyrealsense2 as rs

from cameras.device_manager import find_webcam


def make_session_dirs(output_root: str) -> dict[str, str]:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = os.path.join(output_root, f"session_{timestamp}")

    dirs = {
        "session": session_dir,
        "rs_rgb": os.path.join(session_dir, "rgb_realsense"),
        "webcam_rgb": os.path.join(session_dir, "rgb_webcam"),
        "depth": os.path.join(session_dir, "depth"),
        "combined": os.path.join(session_dir, "combined_npz"),
    }

    for path in dirs.values():
        os.makedirs(path, exist_ok=True)

    return dirs


def configure_realsense(width: int, height: int, fps: int) -> tuple[Any, Any]:
    # Try requested FPS first, then low-FPS options, then common compatibility fallbacks.
    fps_attempts = [fps] + [x for x in (10, 9, 8, 15, 30) if x != fps]

    pipeline = rs.pipeline()
    last_error = None

    for fps_value in fps_attempts:
        config = rs.config()
        config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, fps_value)
        config.enable_stream(rs.stream.depth, width, height, rs.format.z16, fps_value)
        try:
            pipeline.start(config)
            print(f"RealSense FPS: {fps_value}")
            break
        except RuntimeError as err:
            last_error = err
    else:
        raise RuntimeError(f"Unable to start RealSense at 10/9/8/15/30 FPS: {last_error}")

    # Align depth to color so RGB/depth share the same pixel geometry.
    align = rs.align(rs.stream.color)
    return pipeline, align


def configure_webcam(device_path: str, width: int, height: int) -> cv2.VideoCapture:
    cap = cv2.VideoCapture(device_path, cv2.CAP_V4L2)
    if not cap.isOpened():
        raise RuntimeError(f"Unable to open webcam device: {device_path}")

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    return cap


def save_iteration(dirs: dict[str, str], ts_ns: int, rs_rgb: np.ndarray, webcam_rgb: np.ndarray, depth: np.ndarray) -> None:
    frame_id = str(ts_ns)

    cv2.imwrite(os.path.join(dirs["rs_rgb"], f"{frame_id}.png"), rs_rgb)
    cv2.imwrite(os.path.join(dirs["webcam_rgb"], f"{frame_id}.png"), webcam_rgb)
    np.save(os.path.join(dirs["depth"], f"{frame_id}.npy"), depth)

    np.savez_compressed(
        os.path.join(dirs["combined"], f"{frame_id}.npz"),
        rs_rgb=rs_rgb,
        webcam_rgb=webcam_rgb,
        depth=depth,
        timestamp=ts_ns,
    )


class AsyncSaver:

    def __init__(self, dirs: dict[str, str]):
        self.dirs = dirs
        self.queue = queue.Queue(maxsize=4)
        self.running = False
        self.thread = None
        self.dropped = 0
        self.last_error = None

    def start(self) -> None:
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def submit(self, ts_ns: int, rs_rgb: np.ndarray, webcam_rgb: np.ndarray, depth: np.ndarray) -> None:
        try:
            self.queue.put_nowait((ts_ns, rs_rgb, webcam_rgb, depth))
        except queue.Full:
            self.dropped += 1

    def _run(self) -> None:
        while self.running or not self.queue.empty():
            try:
                item = self.queue.get(timeout=0.1)
            except queue.Empty:
                continue

            try:
                ts_ns, rs_rgb, webcam_rgb, depth = item
                save_iteration(self.dirs, ts_ns, rs_rgb, webcam_rgb, depth)
            except Exception as err:
                self.last_error = err
                self.running = False
                break

    def stop(self) -> None:
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join()
        self.thread = None


def main() -> None:
    parser = argparse.ArgumentParser(description="Synchronized RealSense + webcam capture")
    parser.add_argument("--fps", type=int, choices=[8, 9, 10], default=10, help="Capture FPS (8, 9, or 10)")
    args = parser.parse_args()

    width, height, fps = 640, 480, args.fps
    output_root = os.getenv("GMA_RECORDINGS_DIR", "recordings")
    dirs = make_session_dirs(output_root)

    webcam_device = find_webcam()
    if webcam_device is None:
        raise RuntimeError("No USB webcam found")

    pipeline = None
    align = None
    webcam = None
    saver = AsyncSaver(dirs)

    print(f"Saving session to: {dirs['session']}")
    print("Press 'q' to stop")

    try:
        pipeline, align = configure_realsense(width, height, fps)
        webcam = configure_webcam(webcam_device, width, height)
        saver.start()

        while True:
            # Synchronization strategy:
            # 1) Mark start time before both acquisitions.
            # 2) Grab RealSense frames, then webcam frame immediately after.
            # 3) Mark end time and use midpoint as one shared timestamp.
            # This keeps the assigned timestamp centered across all captures.
            t0_ns = time.perf_counter_ns()

            frames = pipeline.wait_for_frames(timeout_ms=1000)
            aligned = align.process(frames)

            rs_color_frame = aligned.get_color_frame()
            rs_depth_frame = aligned.get_depth_frame()
            ok_webcam, webcam_frame = webcam.read()

            t1_ns = time.perf_counter_ns()
            shared_ts_ns = (t0_ns + t1_ns) // 2

            if not rs_color_frame or not rs_depth_frame or not ok_webcam:
                print("Warning: missing frame(s), skipping this iteration")
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
                continue

            rs_rgb = np.asanyarray(rs_color_frame.get_data())
            depth = np.asanyarray(rs_depth_frame.get_data())
            webcam_rgb = np.asanyarray(webcam_frame)

            if rs_rgb.shape[:2] != (height, width):
                rs_rgb = cv2.resize(rs_rgb, (width, height), interpolation=cv2.INTER_LINEAR)

            if depth.shape[:2] != (height, width):
                depth = cv2.resize(depth, (width, height), interpolation=cv2.INTER_NEAREST)

            if webcam_rgb.shape[:2] != (height, width):
                webcam_rgb = cv2.resize(webcam_rgb, (width, height), interpolation=cv2.INTER_LINEAR)

            saver.submit(shared_ts_ns, rs_rgb, webcam_rgb, depth)

            depth_vis = cv2.applyColorMap(
                cv2.convertScaleAbs(depth, alpha=0.03),
                cv2.COLORMAP_JET,
            )

            cv2.imshow("RealSense RGB", rs_rgb)
            cv2.imshow("Webcam RGB", webcam_rgb)
            cv2.imshow("Depth Colormap", depth_vis)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        saver.stop()
        if webcam is not None:
            webcam.release()
        if pipeline is not None:
            try:
                pipeline.stop()
            except Exception:
                pass
        cv2.destroyAllWindows()
        if saver.dropped:
            print(f"Dropped {saver.dropped} pending save tasks because disk I/O could not keep up")
        if saver.last_error is not None:
            print(f"Background save error: {saver.last_error}")
        print(f"Session saved: {dirs['session']}")


if __name__ == "__main__":
    main()
