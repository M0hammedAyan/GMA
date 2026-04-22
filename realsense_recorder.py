"""Color-only RealSense recorder helper."""

import argparse
import queue
import threading
import time
from pathlib import Path
from typing import Any, Optional, cast

import cv2
import numpy as np

try:
    import pyrealsense2 as _rs
except ImportError:
    _rs = None

rs_api = cast(Any, _rs)
cv2_api = cast(Any, cv2)


class RealSenseRecorder:
    def __init__(self, output_dir: str = ".", codec: str = "MJPG") -> None:
        if rs_api is None:
            raise RuntimeError("pyrealsense2 is not installed")

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.output_path = str(self.output_dir / "color_output.avi")
        self.codec = codec

        self.pipeline = rs_api.pipeline()
        self.profile = None

        self.capture_fps = 30
        self.width = 0
        self.height = 0

        self.queue: queue.Queue[np.ndarray] = queue.Queue(maxsize=30)
        self.stop_event = threading.Event()
        self.capture_thread: Optional[threading.Thread] = None
        self.record_thread: Optional[threading.Thread] = None
        self.writer: Any = None

        self.capture_count = 0
        self.record_count = 0
        self.last_error: Optional[Exception] = None
        self._start_time = 0.0

    def _start_pipeline(self) -> None:
        attempts = [
            ((1280, 720, 30), "color 1280x720@30"),
            ((1280, 720, 15), "color 1280x720@15"),
        ]

        ctx = rs_api.context()
        devices = ctx.query_devices()
        if len(devices) == 0:
            raise RuntimeError("RealSense device not detected")

        serial = devices[0].get_info(rs_api.camera_info.serial_number)
        last_error: Optional[Exception] = None

        for (width, height, fps), label in attempts:
            config = rs_api.config()
            config.enable_device(serial)
            config.enable_stream(rs_api.stream.color, width, height, rs_api.format.bgr8, fps)
            try:
                self.profile = self.pipeline.start(config)
                color_profile = self.profile.get_stream(rs_api.stream.color).as_video_stream_profile()
                self.width = int(color_profile.width())
                self.height = int(color_profile.height())
                self.capture_fps = int(color_profile.fps())
                print(f"RealSense profile selected: {label}")
                print(f"Resolution color={self.width}x{self.height} fps={self.capture_fps}")
                return
            except Exception as err:
                last_error = err
                try:
                    self.pipeline.stop()
                except Exception:
                    pass
                time.sleep(0.15)

        raise RuntimeError(f"Could not start RealSense pipeline: {last_error}")

    def _enqueue_drop_oldest(self, item: np.ndarray) -> None:
        if self.queue.full():
            try:
                self.queue.get_nowait()
            except queue.Empty:
                pass

        try:
            self.queue.put_nowait(item)
        except queue.Full:
            pass

    def _capture_loop(self) -> None:
        try:
            while not self.stop_event.is_set():
                try:
                    frames = self.pipeline.wait_for_frames(timeout_ms=1000)
                except RuntimeError:
                    continue

                color_frame = frames.get_color_frame()
                if not color_frame:
                    continue

                color = np.asanyarray(color_frame.get_data()).copy()
                if color.size == 0:
                    continue

                self._enqueue_drop_oldest(color)
                self.capture_count += 1
        except Exception as err:
            self.last_error = err
            self.stop_event.set()

    def _init_writer(self, frame: np.ndarray) -> None:
        if self.writer is not None:
            return

        h, w = frame.shape[:2]
        for codec in (self.codec, "XVID"):
            fourcc = cv2_api.VideoWriter_fourcc(*codec)
            writer = cv2_api.VideoWriter(self.output_path, fourcc, float(self.capture_fps), (w, h))
            if writer.isOpened():
                self.writer = writer
                print(f"Writing color video -> {self.output_path} codec={codec} fps={self.capture_fps}")
                return

        raise RuntimeError(f"Failed to open video writer: {self.output_path}")

    def _record_loop(self) -> None:
        try:
            while not self.stop_event.is_set() or not self.queue.empty():
                try:
                    frame = self.queue.get(timeout=0.2)
                except queue.Empty:
                    continue

                self._init_writer(frame)
                self.writer.write(frame)
                self.record_count += 1
        except Exception as err:
            self.last_error = err
            self.stop_event.set()
        finally:
            if self.writer is not None:
                self.writer.release()
                self.writer = None

    def start(self) -> None:
        self._start_pipeline()
        self.stop_event.clear()
        self.last_error = None
        self._start_time = time.monotonic()

        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.record_thread = threading.Thread(target=self._record_loop, daemon=True)
        self.capture_thread.start()
        self.record_thread.start()

    def stop(self) -> None:
        self.stop_event.set()
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=2.0)
        if self.record_thread and self.record_thread.is_alive():
            self.record_thread.join(timeout=3.0)
        self.capture_thread = None
        self.record_thread = None

        try:
            self.pipeline.stop()
        except Exception:
            pass

    def stats(self) -> str:
        elapsed = max(1e-6, time.monotonic() - self._start_time)
        return (
            f"capture_fps={self.capture_count / elapsed:.2f} "
            f"record_fps={self.record_count / elapsed:.2f} "
            f"resolution={self.width}x{self.height}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Record RealSense color only")
    parser.add_argument("--output-dir", default="recordings", help="Output directory")
    args = parser.parse_args()

    recorder = RealSenseRecorder(args.output_dir)
    try:
        recorder.start()
        print("Recording started. Press Ctrl+C to stop.")
        while True:
            time.sleep(2.0)
            print(recorder.stats())
    except KeyboardInterrupt:
        pass
    finally:
        recorder.stop()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
