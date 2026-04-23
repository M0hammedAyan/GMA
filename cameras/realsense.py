# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportMissingParameterType=false, reportGeneralTypeIssues=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

import os
import queue
import threading
import time

import cv2
import numpy as np

try:
    import pyrealsense2 as rs
except ImportError:
    rs = None

try:
    import psutil
except ImportError:
    psutil = None


def _process_ram_mb():
    if psutil is None:
        return -1.0
    try:
        return psutil.Process().memory_info().rss / (1024 * 1024)
    except Exception:
        return -1.0


class AdaptiveLoadController:
    def __init__(self, base_fps: int):
        self.base_fps = max(1, int(base_fps))
        self.level = 0
        self.overload_count = 0
        self.stable_count = 0
        self.last_eval = 0.0
        self._lock = threading.Lock()

    def _target_fps_for_level(self) -> int:
        if self.level <= 0:
            return self.base_fps
        if self.level == 1:
            return max(20, self.base_fps - 5)
        if self.level == 2:
            return max(18, self.base_fps - 10)
        return max(15, self.base_fps - 15)

    def depth_enabled(self) -> bool:
        with self._lock:
            return self.level <= 1

    def target_record_fps(self) -> int:
        with self._lock:
            return self._target_fps_for_level()

    def evaluate(self, capture_q_size: int, record_q_size: int, q_max: int, avg_proc_ms: float):
        now = time.monotonic()
        with self._lock:
            if now - self.last_eval < 1.0:
                return
            self.last_eval = now

            overload = (
                capture_q_size >= int(q_max * 0.95)
                or record_q_size >= int(q_max * 0.95)
                or avg_proc_ms > 60.0
            )
            stable = capture_q_size <= int(q_max * 0.1) and record_q_size <= int(q_max * 0.1) and avg_proc_ms < 20.0

            if overload:
                self.overload_count += 1
                self.stable_count = 0
            elif stable:
                self.stable_count += 1
                self.overload_count = 0
            else:
                self.overload_count = 0
                self.stable_count = 0

            if self.overload_count >= 3 and self.level < 3:
                self.level += 1
                self.overload_count = 0
                print(f"AdaptiveLoad: overload detected -> level={self.level} target_record_fps={self._target_fps_for_level()}")

            if self.stable_count >= 6 and self.level > 0:
                self.level -= 1
                self.stable_count = 0
                print(f"AdaptiveLoad: stable -> level={self.level} target_record_fps={self._target_fps_for_level()}")


class CaptureWorker(threading.Thread):
    def __init__(self, pipeline, frame_queue, stop_event, on_error, on_runtime_error, delay_threshold_ms=200.0):
        super().__init__(daemon=True)
        self.pipeline = pipeline
        self.frame_queue = frame_queue
        self.stop_event = stop_event
        self.on_error = on_error
        self.on_runtime_error = on_runtime_error
        self.delay_threshold_ms = float(delay_threshold_ms)

        self.capture_frames = 0
        self.drop_new = 0
        self.drop_old = 0
        self.proc_ms_sum = 0.0
        self.started_at = 0.0
        self.last_log = 0.0

    def _enqueue_with_delay_policy(self, item):
        # Keep only the most recent capture when processing lags.
        try:
            self.frame_queue.put_nowait(item)
            return
        except queue.Full:
            pass

        try:
            _ = self.frame_queue.get_nowait()
            self.drop_old += 1
        except queue.Empty:
            self.drop_new += 1
            return

        while not self.stop_event.is_set():
            try:
                self.frame_queue.put(item, timeout=0.02)
                return
            except queue.Full:
                continue

    def _log_stats(self):
        now = time.monotonic()
        if now - self.last_log < 1.0:
            return
        elapsed = max(1e-6, now - self.started_at)
        fps = self.capture_frames / elapsed
        avg_ms = self.proc_ms_sum / max(1, self.capture_frames)
        ram_mb = _process_ram_mb()
        ram_text = f"{ram_mb:.1f}MB" if ram_mb >= 0 else "n/a"
        print(
            f"CaptureWorker fps={fps:.2f} q={self.frame_queue.qsize()}/{self.frame_queue.maxsize} "
            f"drop_old={self.drop_old} drop_new={self.drop_new} avg_loop_ms={avg_ms:.2f} ram={ram_text}"
        )
        self.last_log = now

    def run(self):
        self.started_at = time.monotonic()
        self.last_log = self.started_at

        while not self.stop_event.is_set():
            loop_started = time.perf_counter()
            try:
                frames = self.pipeline.wait_for_frames(timeout_ms=1000)
                capture_ts = time.monotonic()
                self._enqueue_with_delay_policy((frames, capture_ts))
                self.capture_frames += 1
                self.proc_ms_sum += (time.perf_counter() - loop_started) * 1000.0
                self._log_stats()
            except RuntimeError as err:
                print(f"RealSense error: {err}")
                restarted = self.on_runtime_error(err)
                if not restarted:
                    self.on_error(err)
                    self.stop_event.set()
                    break
            except Exception as err:
                self.on_error(err)
                self.stop_event.set()
                break


class ProcessingWorker(threading.Thread):
    def __init__(
        self,
        align,
        capture_queue,
        stop_event,
        adaptive,
        on_preview,
        on_record_frame,
        on_error,
        delay_threshold_ms=200.0,
    ):
        super().__init__(daemon=True)
        self.align = align
        self.capture_queue = capture_queue
        self.stop_event = stop_event
        self.adaptive = adaptive
        self.on_preview = on_preview
        self.on_record_frame = on_record_frame
        self.on_error = on_error
        self.delay_threshold_ms = float(delay_threshold_ms)

        self.processed_frames = 0
        self.preview_disabled_depth = 0
        self.dropped_record_stale = 0
        self.proc_ms_sum = 0.0
        self.started_at = 0.0
        self.last_log = 0.0

    def _log_stats(self):
        now = time.monotonic()
        if now - self.last_log < 1.0:
            return

        elapsed = max(1e-6, now - self.started_at)
        fps = self.processed_frames / elapsed
        avg_ms = self.proc_ms_sum / max(1, self.processed_frames)
        ram_mb = _process_ram_mb()
        ram_text = f"{ram_mb:.1f}MB" if ram_mb >= 0 else "n/a"

        self.adaptive.evaluate(self.capture_queue.qsize(), 0, self.capture_queue.maxsize, avg_ms)

        print(
            f"ProcessingWorker fps={fps:.2f} cap_q={self.capture_queue.qsize()}/{self.capture_queue.maxsize} "
            f"avg_proc_ms={avg_ms:.2f} "
            f"stale_drop={self.dropped_record_stale} depth_enabled={self.adaptive.depth_enabled()} ram={ram_text}"
        )
        self.last_log = now

    def run(self):
        self.started_at = time.monotonic()
        self.last_log = self.started_at

        while not self.stop_event.is_set() or not self.capture_queue.empty():
            try:
                frames, capture_ts = self.capture_queue.get(timeout=0.2)
            except queue.Empty:
                self._log_stats()
                continue

            item_started = time.perf_counter()
            try:
                aligned = self.align.process(frames)
                depth_frame = aligned.get_depth_frame()
                color_frame = aligned.get_color_frame()
                if not depth_frame or not color_frame:
                    self._log_stats()
                    continue

                color = np.asanyarray(color_frame.get_data())
                depth = np.asanyarray(depth_frame.get_data())
                if color is None or depth is None or color.size == 0 or depth.size == 0:
                    self._log_stats()
                    continue

                if len(depth.shape) != 2:
                    depth = depth.reshape(depth.shape[0], depth.shape[1])

                depth_colormap = None
                if self.adaptive.depth_enabled():
                    depth_u8 = cv2.convertScaleAbs(depth, alpha=0.03)
                    if depth_u8 is not None and depth_u8.size > 0:
                        depth_colormap = cv2.applyColorMap(depth_u8, cv2.COLORMAP_JET)
                else:
                    self.preview_disabled_depth += 1

                # Keep copies limited to one processing boundary crossing.
                color_copy = color.copy()
                depth_map_copy = None if depth_colormap is None else depth_colormap.copy()

                self.on_preview(color_copy, depth_map_copy)
                self.on_record_frame(capture_ts, color_copy, depth_map_copy)

                self.processed_frames += 1
                self.proc_ms_sum += (time.perf_counter() - item_started) * 1000.0
                self._log_stats()
            except RuntimeError as err:
                self.on_error(err)
                self.stop_event.set()
                break
            except Exception as err:
                self.on_error(err)
                self.stop_event.set()
                break


class RecorderWorker(threading.Thread):
    def __init__(self, stop_event, color_output_path, depth_output_path, target_fps, frame_source, on_error):
        super().__init__(daemon=True)
        self.stop_event = stop_event
        self.color_output_path = color_output_path
        self.depth_output_path = depth_output_path
        self.target_fps = max(1, int(target_fps))
        self.frame_source = frame_source
        self.on_error = on_error

        self.color_writer = None
        self.depth_writer = None
        self.recorded_frames = 0
        self.write_ms_sum = 0.0
        self.started_at = 0.0
        self.last_log = 0.0
        self._zero_depth_cache = None

    def _init_writers(self, color, depth_colormap, fps):
        if self.color_writer is not None and self.depth_writer is not None:
            return

        h, w = color.shape[:2]
        if depth_colormap is not None and depth_colormap.size > 0:
            dh, dw = depth_colormap.shape[:2]
        else:
            dh, dw = h, w

        for codec in ("MJPG", "XVID"):
            fourcc = cv2.VideoWriter_fourcc(*codec)
            color_writer = cv2.VideoWriter(self.color_output_path, fourcc, float(fps), (w, h))
            depth_writer = cv2.VideoWriter(self.depth_output_path, fourcc, float(fps), (dw, dh))
            if color_writer.isOpened() and depth_writer.isOpened():
                self.color_writer = color_writer
                self.depth_writer = depth_writer
                print(
                    f"RecorderWorker writers opened codec={codec} fps={fps} "
                    f"color={self.color_output_path} depth={self.depth_output_path}"
                )
                return
            color_writer.release()
            depth_writer.release()

        raise RuntimeError("Failed to open RealSense writers")

    def _log_stats(self):
        now = time.monotonic()
        if now - self.last_log < 1.0:
            return

        elapsed = max(1e-6, now - self.started_at)
        fps = self.recorded_frames / elapsed
        avg_ms = self.write_ms_sum / max(1, self.recorded_frames)
        ram_mb = _process_ram_mb()
        ram_text = f"{ram_mb:.1f}MB" if ram_mb >= 0 else "n/a"

        print(
            f"RecorderWorker fps={fps:.2f} target={self.target_fps} avg_write_ms={avg_ms:.2f} ram={ram_text}"
        )
        self.last_log = now

    def run(self):
        self.started_at = time.monotonic()
        self.last_log = self.started_at
        frame_interval = 1.0 / float(self.target_fps)
        next_frame_time = time.time()

        try:
            while not self.stop_event.is_set():
                now = time.time()
                if now < next_frame_time:
                    time.sleep(min(0.005, next_frame_time - now))
                    continue

                _capture_ts, color, depth_colormap = self.frame_source()
                if color is None:
                    next_frame_time += frame_interval
                    self._log_stats()
                    continue

                write_started = time.perf_counter()
                self._init_writers(color, depth_colormap, self.target_fps)

                depth_frame = depth_colormap
                if depth_frame is None:
                    if self._zero_depth_cache is None or self._zero_depth_cache.shape[:2] != color.shape[:2]:
                        self._zero_depth_cache = np.zeros_like(color)
                    depth_frame = self._zero_depth_cache

                self.color_writer.write(color)
                self.depth_writer.write(depth_frame)

                self.recorded_frames += 1
                self.write_ms_sum += (time.perf_counter() - write_started) * 1000.0
                self._log_stats()

                next_frame_time += frame_interval
        except Exception as err:
            self.on_error(err)
            self.stop_event.set()
        finally:
            if self.color_writer is not None:
                self.color_writer.release()
                self.color_writer = None
            if self.depth_writer is not None:
                self.depth_writer.release()
                self.depth_writer = None


class RealSenseCamera:
    def __init__(self):
        if rs is None:
            raise RuntimeError(
                "pyrealsense2 is not installed for this Python environment. "
                "Install a compatible wheel or use a Python version supported by pyrealsense2."
            )

        self.pipeline = rs.pipeline()
        self.profile = None
        self.align = rs.align(rs.stream.color)
        self._pipeline_lock = threading.Lock()

        self.running = False
        self.recording = False
        self.path = ""
        self.last_error = None

        self.capture_queue = queue.Queue(maxsize=4)
        self.stop_event = threading.Event()

        self.capture_worker = None
        self.processing_worker = None
        self.recorder_worker = None
        self._capture_thread = None
        self._record_thread = None

        self._preview_lock = threading.Lock()
        self._latest_color = None
        self._latest_depth_colormap = None
        self._record_lock = threading.Lock()
        self._record_latest_color = None
        self._record_latest_depth = None
        self._record_latest_ts = 0.0
        self._record_last_color = None
        self._record_last_depth = None
        self._record_blank_color = None
        self._record_blank_depth = None
        self._record_queue = queue.Queue(maxsize=300)
        self._record_queue_drop = 0
        self._captured_frames = 0
        self._written_frames = 0
        self._dropped_early = 0
        self._dropped_late = 0
        self._rs_hw_base_ts = None
        self._record_started_at = 0.0
        self._record_stop_at = None
        self._record_gate = threading.Event()

        self.base = ""

        self._start_pipeline_with_fallbacks()
        self.adaptive = AdaptiveLoadController(getattr(self, "sensor_fps", 30))

    def _start_pipeline_with_fallbacks(self):
        attempts = [
            ((1920, 1080, 30), (1280, 720, 30), "color 1920x1080@30 + depth 1280x720@30"),
            ((1280, 720, 30), (640, 480, 30), "color 1280x720@30 + depth 640x480@30"),
            ((1280, 720, 15), (640, 480, 15), "color 1280x720@15 + depth 640x480@15"),
            ((640, 480, 30), (640, 480, 30), "color 640x480@30 + depth 640x480@30"),
        ]

        ctx = rs.context()
        devices = ctx.query_devices()
        if len(devices) == 0:
            raise RuntimeError("RealSense device not detected")

        device = devices[0]
        serial = device.get_info(rs.camera_info.serial_number)

        has_rgb_sensor = any(
            "rgb" in sensor.get_info(rs.camera_info.name).lower() for sensor in device.query_sensors()
        )
        if not has_rgb_sensor:
            raise RuntimeError("Connected RealSense device has no RGB sensor; color stream is required")

        last_error = None
        for color_cfg, depth_cfg, label in attempts:
            config = rs.config()
            config.enable_device(serial)
            cw, ch, cfps = color_cfg
            dw, dh, dfps = depth_cfg
            config.enable_stream(rs.stream.color, cw, ch, rs.format.bgr8, cfps)
            config.enable_stream(rs.stream.depth, dw, dh, rs.format.z16, dfps)
            try:
                self.profile = self.pipeline.start(config)
                color_prof = self.profile.get_stream(rs.stream.color).as_video_stream_profile()
                self.width = int(color_prof.width())
                self.height = int(color_prof.height())
                self.sensor_fps = int(color_prof.fps())
                print(f"RealSense profile selected: {label}")
                print(f"Resolution={self.width}x{self.height} FPS={self.sensor_fps}")
                return
            except RuntimeError as err:
                last_error = err
                try:
                    self.pipeline.stop()
                except Exception:
                    pass
                time.sleep(0.15)

        raise RuntimeError(
            "RealSense pipeline start failed for all profiles. "
            f"Last error: {last_error}. Try USB 3.0 port/cable, then rerun."
        )

    def _restart_pipeline(self):
        if self.stop_event.is_set():
            return False

        with self._pipeline_lock:
            try:
                self.pipeline.stop()
            except Exception:
                pass

            try:
                self._start_pipeline_with_fallbacks()
                return True
            except Exception as err:
                self.last_error = err
                return False

    def _on_runtime_error(self, _err):
        return self._restart_pipeline()

    def setup_folders(self, session_path):
        self.base = os.path.join(session_path, "realsense")
        os.makedirs(self.base, exist_ok=True)

    def start(self, video_path, video_fps=30, started_at=None):
        base, _ = os.path.splitext(video_path)
        color_out_path = f"{base}.avi"
        depth_out_path = f"{base}_depth.avi"

        self.video_fps = max(1, int(video_fps))

        with self._record_lock:
            self._record_latest_color = None
            self._record_latest_depth = None
            self._record_latest_ts = 0.0
            self._record_last_color = None
            self._record_last_depth = None
            self._record_blank_color = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            self._record_blank_depth = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        self.stop_event.clear()
        self._record_gate.clear()
        self.last_error = None
        self._record_queue = queue.Queue(maxsize=300)
        self._record_queue_drop = 0
        self._captured_frames = 0
        self._written_frames = 0
        self._dropped_early = 0
        self._dropped_late = 0
        self._rs_hw_base_ts = None
        self.recording = True
        self.running = True
        self.path = color_out_path
        self._record_started_at = time.monotonic() if started_at is None else float(started_at)
        if started_at is not None:
            self._record_gate.set()
        self._record_stop_at = None

        self.capture_worker = threading.Thread(target=self._capture_loop, daemon=True)
        self.recorder_worker = threading.Thread(
            target=self._record_loop,
            args=(color_out_path, depth_out_path),
            daemon=True,
        )

        self.capture_worker.start()
        self.recorder_worker.start()
        print(f"RealSense recording started: color={color_out_path} depth={depth_out_path}")

    def _capture_loop(self):
        while not self.stop_event.is_set():
            try:
                frames = self.pipeline.wait_for_frames(timeout_ms=1000)
            except RuntimeError as err:
                print(f"RealSense error: {err}")
                restarted = self._on_runtime_error(err)
                if not restarted:
                    self._on_worker_error(err)
                    self.stop_event.set()
                    break
                continue
            except Exception as err:
                self._on_worker_error(err)
                self.stop_event.set()
                break

            try:
                aligned = self.align.process(frames)
                depth_frame = aligned.get_depth_frame()
                color_frame = aligned.get_color_frame()
                if not depth_frame or not color_frame:
                    continue

                color = np.asanyarray(color_frame.get_data())
                depth = np.asanyarray(depth_frame.get_data())
                if color is None or depth is None or color.size == 0 or depth.size == 0:
                    continue

                if len(depth.shape) != 2:
                    depth = depth.reshape(depth.shape[0], depth.shape[1])

                depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth, alpha=0.03), cv2.COLORMAP_JET)

                raw_hw_ts_ms = float(color_frame.get_timestamp())
                if self._rs_hw_base_ts is None:
                    self._rs_hw_base_ts = raw_hw_ts_ms
                capture_ts = max(0.0, (raw_hw_ts_ms - self._rs_hw_base_ts) / 1000.0)
            except Exception as err:
                self._on_worker_error(err)
                self.stop_event.set()
                break

            self._captured_frames += 1

            item = (capture_ts, color.copy(), depth_colormap.copy())
            while not self.stop_event.is_set():
                try:
                    self._record_queue.put_nowait(item)
                    break
                except queue.Full:
                    try:
                        _ = self._record_queue.get_nowait()
                        self._record_queue_drop += 1
                    except queue.Empty:
                        break

            with self._record_lock:
                self._record_latest_color = color.copy()
                self._record_latest_depth = depth_colormap.copy()
                self._record_latest_ts = capture_ts

            with self._preview_lock:
                self._latest_color = color.copy()
                self._latest_depth_colormap = depth_colormap.copy()

    def _prepare_latest_frames(self):
        with self._record_lock:
            if self._record_latest_color is None:
                return None, None, None
            capture_ts = self._record_latest_ts
            color = self._record_latest_color.copy()
            depth_colormap = None if self._record_latest_depth is None else self._record_latest_depth.copy()

        if color is None:
            return None, None, None
        return capture_ts, color, depth_colormap

    def _record_loop(self, color_out_path, depth_out_path):
        write_fps = float(max(1, int(self.video_fps)))
        frame_interval = 1.0 / write_fps
        start_wall = None
        next_frame_time = None
        expected_frames = 0

        color_writer = None
        depth_writer = None

        def _open_writers(sample_color, sample_depth):
            h, w = sample_color.shape[:2]
            dh, dw = sample_depth.shape[:2] if sample_depth is not None else (h, w)

            for codec in ("MJPG", "XVID"):
                fourcc = cv2.VideoWriter_fourcc(*codec)
                temp_color_writer = cv2.VideoWriter(color_out_path, fourcc, write_fps, (w, h))
                temp_depth_writer = cv2.VideoWriter(depth_out_path, fourcc, write_fps, (dw, dh))
                if temp_color_writer.isOpened() and temp_depth_writer.isOpened():
                    color_writer = temp_color_writer
                    depth_writer = temp_depth_writer
                    print(
                        f"RealSense writers opened codec={codec} fps={write_fps:.2f} "
                        f"color={color_out_path} depth={depth_out_path}"
                    )
                    return color_writer, depth_writer
                temp_color_writer.release()
                temp_depth_writer.release()

            raise RuntimeError("Failed to open RealSense writers")

        def _drain_latest_item():
            latest = None
            while True:
                try:
                    latest = self._record_queue.get_nowait()
                except queue.Empty:
                    break
            return latest

        try:
            while True:
                if not self._record_gate.is_set():
                    time.sleep(0.002)
                    continue

                if color_writer is None or depth_writer is None:
                    item = _drain_latest_item()
                    if item is None:
                        if self.stop_event.is_set():
                            break
                        time.sleep(0.01)
                        continue
                    _capture_ts, color, depth_colormap = item
                    color_writer, depth_writer = _open_writers(color, depth_colormap)
                    start_wall = time.monotonic()
                    next_frame_time = start_wall

                if next_frame_time is None:
                    next_frame_time = time.monotonic()

                now = time.monotonic()
                if now < next_frame_time:
                    time.sleep(min(0.01, next_frame_time - now))
                    continue

                item = _drain_latest_item()
                expected_frames += 1
                if item is None:
                    next_frame_time += frame_interval
                    if self.stop_event.is_set() and self._record_queue.empty():
                        break
                    continue

                _capture_ts, color, depth_colormap = item

                depth_frame = depth_colormap
                if depth_frame is None:
                    depth_frame = self._record_blank_depth.copy() if self._record_blank_depth is not None else np.zeros_like(color)

                with self._record_lock:
                    self._record_last_color = color.copy()
                    self._record_last_depth = depth_frame.copy()

                color_writer.write(color)
                depth_writer.write(depth_frame)
                self._written_frames += 1
                next_frame_time += frame_interval
        except Exception as err:
            self._on_worker_error(err)
            self.stop_event.set()
        finally:
            if color_writer is not None:
                color_writer.release()
            if depth_writer is not None:
                depth_writer.release()
            duration_real = 0.0 if start_wall is None else max(0.0, time.monotonic() - start_wall)
            duration_video = 0.0 if write_fps <= 0 else (self._written_frames / write_fps)
            effective_fps = 0.0 if duration_real <= 0 else (float(self._written_frames) / duration_real)
            print(
                "RealSense timing stats: "
                f"captured={self._captured_frames} written={self._written_frames} "
                f"expected={expected_frames} dropped_queue={self._record_queue_drop} "
                f"writer_fps={write_fps:.2f} effective_fps={effective_fps:.2f} "
                f"real_s={duration_real:.2f} video_s={duration_video:.2f}"
            )

    def _on_worker_error(self, err):
        self.last_error = err
        self.stop_event.set()

    def _update_latest_frames(self, color, depth_colormap):
        with self._preview_lock:
            self._latest_color = None if color is None else color.copy()
            self._latest_depth_colormap = None if depth_colormap is None else depth_colormap.copy()

    def capture(self):
        return

    def get_latest_preview_frames(self):
        with self._preview_lock:
            color = None if self._latest_color is None else self._latest_color.copy()
            depth = None if self._latest_depth_colormap is None else self._latest_depth_colormap.copy()

        if color is None and depth is None and self.last_error is not None:
            return None, None

        return color, depth

    def set_recording_start_time(self, started_at):
        self._record_started_at = float(started_at)
        self._record_gate.set()

    def set_recording_stop_time(self, stop_at):
        self._record_stop_at = float(stop_at)

    def request_stop(self):
        self.stop_event.set()

    def stop(self):
        self.running = False
        self.recording = False
        if self._record_stop_at is None:
            self._record_stop_at = time.monotonic()
        self.stop_event.set()

        pipeline_stopped = False
        if self.capture_worker is not None and self.capture_worker.is_alive():
            try:
                self.pipeline.stop()
                pipeline_stopped = True
            except Exception:
                pass

        if self.capture_worker is not None and self.capture_worker.is_alive():
            self.capture_worker.join()
        if self.recorder_worker is not None and self.recorder_worker.is_alive():
            self.recorder_worker.join()

        self.capture_worker = None
        self.recorder_worker = None

        if not pipeline_stopped:
            try:
                self.pipeline.stop()
            except Exception:
                pass

        with self._preview_lock:
            self._latest_color = None
            self._latest_depth_colormap = None
        with self._record_lock:
            self._record_latest_color = None
            self._record_latest_depth = None
            self._record_latest_ts = 0.0
        while True:
            try:
                _ = self._record_queue.get_nowait()
            except queue.Empty:
                break
