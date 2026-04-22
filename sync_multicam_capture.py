import argparse
import os
from datetime import datetime
from pathlib import Path
from typing import Any, cast

import cv2
import numpy as np
import pyrealsense2 as _rs

rs_api = cast(Any, _rs)
cv2_api = cast(Any, cv2)


def _make_session_dir(output_root: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = Path(output_root) / f"session_{timestamp}"
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir


def _open_writer(path: Path, fps: int, frame_width: int, frame_height: int):
    for codec in ("MJPG", "XVID"):
        fourcc = cv2_api.VideoWriter_fourcc(*codec)
        writer = cv2_api.VideoWriter(str(path), fourcc, float(fps), (frame_width, frame_height))
        if writer.isOpened():
            print(f"Writer opened: {path} codec={codec} fps={fps} size={frame_width}x{frame_height}")
            return writer
    raise RuntimeError(f"Unable to open video writer: {path}")


def _start_pipeline(width: int, height: int, fps: int):
    ctx = rs_api.context()
    devices = ctx.query_devices()
    if len(devices) == 0:
        raise RuntimeError("RealSense device not detected")

    serial = devices[0].get_info(rs_api.camera_info.serial_number)
    attempts = [fps] + [candidate for candidate in (30, 15) if candidate != fps]
    last_error = None

    pipeline = rs_api.pipeline()
    for candidate_fps in attempts:
        config = rs_api.config()
        config.enable_device(serial)
        config.enable_stream(rs_api.stream.color, width, height, rs_api.format.bgr8, candidate_fps)
        try:
            profile = pipeline.start(config)
            color_profile = profile.get_stream(rs_api.stream.color).as_video_stream_profile()
            print(
                f"RealSense color stream: {int(color_profile.width())}x{int(color_profile.height())}"
                f"@{int(color_profile.fps())}"
            )
            return pipeline, profile
        except RuntimeError as err:
            last_error = err
            try:
                pipeline.stop()
            except Exception:
                pass
            # Try lower resolution if higher fails
            if width > 1280:
                width = 1280
            elif width > 640:
                width = 640
            height = (height * width) // 1920 if width <= 1280 else (height * width) // 1280

    raise RuntimeError(f"Unable to start RealSense color stream: {last_error}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture RealSense color only")
    parser.add_argument("--fps", type=int, default=30, help="Target capture FPS")
    parser.add_argument("--output-root", default=os.getenv("GMA_RECORDINGS_DIR", "recordings"), help="Output root directory")
    args = parser.parse_args()

    width, height = 1920, 1080
    session_dir = _make_session_dir(args.output_root)
    output_path = session_dir / "realsense.avi"

    pipeline = None
    writer = None
    try:
        pipeline, profile = _start_pipeline(width, height, args.fps)
        fps = int(profile.get_stream(rs_api.stream.color).as_video_stream_profile().fps())
        fps = max(1, fps)

        print(f"Saving session to: {session_dir}")
        print("Press q to stop")

        while True:
            frames = pipeline.wait_for_frames(timeout_ms=1000)
            color_frame = frames.get_color_frame()
            if not color_frame:
                continue

            color = np.asanyarray(color_frame.get_data()).copy()
            if color.size == 0:
                continue

            if writer is None:
                writer = _open_writer(output_path, fps, color.shape[1], color.shape[0])

            writer.write(color)
            cv2_api.imshow("RealSense Color", color)
            if cv2_api.waitKey(1) & 0xFF == ord("q"):
                break

    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        if writer is not None:
            writer.release()
        if pipeline is not None:
            try:
                pipeline.stop()
            except Exception:
                pass
        cv2_api.destroyAllWindows()
        print(f"Session saved: {session_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
