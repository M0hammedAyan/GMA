import pyrealsense2 as rs
import numpy as np
import cv2
import time

# RealSense D435 live viewer.
# On USB3: show color stream.
# On USB2 (no reliable color bandwidth): show a single infrared stream for smooth monochrome video.


def get_device():
    ctx = rs.context()
    if not ctx.devices:
        raise RuntimeError("No RealSense device detected.")
    return ctx, ctx.devices[0]


def bus_speed(device):
    return "USB2" if device.get_info(rs.camera_info.usb_type_descriptor).startswith("2") else "USB3"


def enumerate_color_profiles(device, bus):
    """
    Read color profiles from the device and prefer lowest bandwidth first.
    """
    allowed_formats = [rs.format.yuyv, rs.format.bgr8, rs.format.rgb8]  # YUYV is lighter than BGR8
    profiles = []
    for sensor in device.query_sensors():
        for p in sensor.get_stream_profiles():
            vsp = p.as_video_stream_profile()
            fmt = vsp.format()
            if vsp.stream_type() != rs.stream.color or fmt not in allowed_formats:
                continue
            w, h, fps = vsp.width(), vsp.height(), vsp.fps()
            if bus == "USB2" and fps > 15:
                continue
            if w > 1280 or h > 720:
                continue
            profiles.append((w, h, fps, fmt))

    if not profiles:
        raise RuntimeError("No suitable color profiles found.")

    # Deduplicate by (w,h,fps) keeping the lightest format first.
    seen = {}
    for w, h, fps, fmt in profiles:
        key = (w, h, fps)
        if key not in seen or allowed_formats.index(fmt) < allowed_formats.index(seen[key][3]):
            seen[key] = (w, h, fps, fmt)

    profiles = list(seen.values())
    # Sort by bandwidth: fps then area (smallest first)
    profiles.sort(key=lambda x: (x[2], x[0] * x[1]))
    return profiles


def start_color_pipeline(color_profile, serial=None):
    cfg = rs.config()
    w, h, fps, fmt = color_profile
    if serial:
        cfg.enable_device(serial)
    cfg.enable_stream(rs.stream.color, w, h, fmt, fps)

    pipe = rs.pipeline()
    profile = pipe.start(cfg)

    try:
        color_sensor = profile.get_device().first_color_sensor()
        color_sensor.set_option(rs.option.frames_queue_size, 1)
        if color_sensor.supports(rs.option.auto_exposure_priority):
            color_sensor.set_option(rs.option.auto_exposure_priority, 0)
    except Exception:
        pass

    return pipe


def start_ir_pipeline(ir_index, profile, serial=None):
    cfg = rs.config()
    if serial:
        cfg.enable_device(serial)
    w, h, fps = profile
    cfg.enable_stream(rs.stream.infrared, ir_index, w, h, rs.format.y8, fps)
    pipe = rs.pipeline()
    prof = pipe.start(cfg)
    try:
        ir_sensor = prof.get_device().first_depth_sensor()
        ir_sensor.set_option(rs.option.frames_queue_size, 1)
    except Exception:
        pass
    return pipe


def describe(color, bus):
    fmt_name = {rs.format.yuyv: "YUYV", rs.format.bgr8: "BGR8", rs.format.rgb8: "RGB8"}.get(color[3], str(color[3]))
    c = f"color {color[0]}x{color[1]}@{color[2]} {fmt_name}"
    print(f"Trying on {bus}: {c}")


def run_viewer():
    ctx, device = get_device()
    serial = device.get_info(rs.camera_info.serial_number)
    bus = bus_speed(device)
    print(f"Detected device {serial} on {bus}")

    # One hardware reset to clear stuck state, then recreate context/device.
    try:
        print("Resetting camera...")
        device.hardware_reset()
        time.sleep(3)
        ctx, device = get_device()
        serial = device.get_info(rs.camera_info.serial_number)
        bus = bus_speed(device)
        print(f"Back after reset: {serial} on {bus}")
    except Exception as e:
        print(f"Hardware reset skipped/failed: {e}")

    # If USB2, go straight to IR which is reliable on low bandwidth.
    if bus == "USB2":
        print("USB2 detected: using infrared stream for smooth video.")
        ir_profiles = [
            (640, 480, 15),
            (424, 240, 15),
            (424, 240, 6),
            (320, 240, 15),
        ]
        ir_indexes = [1, 2]  # left / right IR streams
        for ir_idx in ir_indexes:
            for prof in ir_profiles:
                print(f"Trying IR{ir_idx} {prof[0]}x{prof[1]}@{prof[2]}")
                try:
                    pipe = start_ir_pipeline(ir_idx, prof, serial=serial)
                except RuntimeError as e:
                    print(f"IR start failed: {e}")
                    continue
                try:
                    timeouts = 0
                    while True:
                        try:
                            frames = pipe.wait_for_frames(timeout_ms=8000)
                        except RuntimeError as e:
                            timeouts += 1
                            print(f"Timeout {timeouts} on IR{ir_idx} {prof}: {e}")
                            if timeouts >= 3:
                                break
                            continue
                        timeouts = 0
                        ir_frame = frames.get_infrared_frame(ir_idx)
                        if not ir_frame:
                            continue
                        ir_image = np.asanyarray(ir_frame.get_data())
                        cv2.imshow("RealSense D435 (Infrared)", ir_image)
                        if cv2.waitKey(1) & 0xFF == ord("q"):
                            return
                finally:
                    try:
                        pipe.stop()
                    except Exception:
                        pass
        raise RuntimeError("Unable to capture infrared frames on USB2.")

    # USB3 path: try color profiles
    candidates = enumerate_color_profiles(device, bus)

    for color in candidates:
        describe(color, bus)
        try:
            pipe = start_color_pipeline(color, serial=serial)
        except RuntimeError as e:
            print(f"Start failed: {e}")
            continue

        try:
            timeouts = 0
            timeout_ms = 8000
            while True:
                try:
                    frames = pipe.wait_for_frames(timeout_ms=timeout_ms)
                except RuntimeError as e:
                    timeouts += 1
                    print(f"Timeout {timeouts} on profile: {e}")
                    if timeouts >= 3:
                        break
                    continue

                timeouts = 0
                color_frame = frames.get_color_frame()
                if not color_frame:
                    continue

                color_image = np.asanyarray(color_frame.get_data())
                cv2.imshow("RealSense D435 (Color)", color_image)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    return
        finally:
            try:
                pipe.stop()
            except Exception:
                pass

    raise RuntimeError("Unable to capture color frames on available profiles.")


if __name__ == "__main__":
    run_viewer()
