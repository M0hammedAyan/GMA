import argparse
import bisect
import glob
from pathlib import Path

import cv2
import numpy as np


def list_sessions(recordings_root: str) -> list[Path]:
    return sorted(Path(recordings_root).glob("session_*"))


def find_latest_session(recordings_root: str) -> Path:
    sessions = list_sessions(recordings_root)
    if not sessions:
        raise FileNotFoundError(f"No sessions found in {recordings_root}")
    return sessions[-1]


def sorted_files(pattern: str) -> list[str]:
    return sorted(glob.glob(pattern))


def stem_index(path: str, fallback: int) -> int:
    try:
        return int(Path(path).stem)
    except ValueError:
        return fallback


def resolve_layout(session_dir: Path) -> dict:
    # Layout A (Recorder class output)
    rs_rgb_a = session_dir / "realsense" / "rgb"
    depth_a = session_dir / "realsense" / "depth"
    pc_a = session_dir / "realsense" / "pointcloud"
    rs_mp4_a = session_dir / "realsense.mp4"
    rs_avi_a = session_dir / "realsense.avi"
    webcam_mp4_a = session_dir / "webcam.mp4"
    webcam_avi_a = session_dir / "webcam.avi"

    # Layout B (sync_multicam_capture.py output)
    rs_rgb_b = session_dir / "rgb_realsense"
    webcam_rgb_b = session_dir / "rgb_webcam"
    depth_b = session_dir / "depth"
    pc_b = session_dir / "pointcloud"

    if rs_rgb_a.exists() and depth_a.exists():
        realsense_video = ""
        if rs_avi_a.exists():
            realsense_video = str(rs_avi_a)
        elif rs_mp4_a.exists():
            realsense_video = str(rs_mp4_a)

        webcam_video = ""
        if webcam_avi_a.exists():
            webcam_video = str(webcam_avi_a)
        elif webcam_mp4_a.exists():
            webcam_video = str(webcam_mp4_a)

        return {
            "rs_rgb_files": sorted_files(str(rs_rgb_a / "*.png")),
            "depth_files": sorted_files(str(depth_a / "*.npy")),
            "pointcloud_files": sorted_files(str(pc_a / "*.npz")) if pc_a.exists() else [],
            "realsense_video": realsense_video,
            "webcam_mode": "video" if webcam_video else "none",
            "webcam_video": webcam_video,
            "webcam_files": [],
        }

    if rs_rgb_b.exists() and depth_b.exists():
        return {
            "rs_rgb_files": sorted_files(str(rs_rgb_b / "*.png")),
            "depth_files": sorted_files(str(depth_b / "*.npy")),
            "pointcloud_files": sorted_files(str(pc_b / "*.npz")) if pc_b.exists() else [],
            "realsense_video": "",
            "webcam_mode": "images" if webcam_rgb_b.exists() else "none",
            "webcam_video": "",
            "webcam_files": sorted_files(str(webcam_rgb_b / "*.png")) if webcam_rgb_b.exists() else [],
        }

    raise FileNotFoundError(
        f"Unsupported session layout in {session_dir}. "
        "Expected either realsense/rgb+depth or rgb_realsense+depth."
    )


def find_latest_playable_layout(recordings_root: str) -> tuple[Path, dict]:
    sessions = list_sessions(recordings_root)
    if not sessions:
        raise FileNotFoundError(f"No sessions found in {recordings_root}")

    # Walk newest to oldest and pick the first session with a supported, non-empty layout.
    for session_dir in reversed(sessions):
        try:
            layout = resolve_layout(session_dir)
        except FileNotFoundError:
            continue

        if layout["rs_rgb_files"] and layout["depth_files"]:
            return session_dir, layout

    raise FileNotFoundError(
        f"No playable sessions found in {recordings_root}. "
        "Expected rgb/depth files in one of the supported layouts."
    )


def depth_to_colormap(depth: np.ndarray) -> np.ndarray:
    return cv2.applyColorMap(cv2.convertScaleAbs(depth, alpha=0.03), cv2.COLORMAP_JET)


def create_open3d_visualizer(enable_pc: bool):
    if not enable_pc:
        return None, None, None

    try:
        import open3d as o3d
    except Exception:
        print("Open3D not installed; point cloud viewer disabled.")
        return None, None, None

    vis = o3d.visualization.Visualizer()
    vis.create_window(window_name="PointCloud", width=960, height=540, visible=True)
    pcd = o3d.geometry.PointCloud()
    vis.add_geometry(pcd)
    return o3d, vis, pcd


def update_open3d(o3d_mod, vis, pcd, npz_path: str) -> None:
    if not npz_path:
        return

    try:
        data = np.load(npz_path)
        xyz = data["xyz"]
        rgb = data["rgb"]

        if xyz.ndim != 2 or xyz.shape[1] != 3:
            return
        if rgb.ndim != 2 or rgb.shape[1] != 3:
            return

        pcd.points = o3d_mod.utility.Vector3dVector(xyz.astype(np.float64))
        pcd.colors = o3d_mod.utility.Vector3dVector(np.clip(rgb.astype(np.float64), 0.0, 1.0))
        vis.update_geometry(pcd)
        vis.poll_events()
        vis.update_renderer()
    except Exception as err:
        print(f"Point cloud update failed for {npz_path}: {err}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Play RealSense RGB, webcam, depth colormap, and optional point cloud from a session"
    )
    parser.add_argument("--session", default="", help="Path to a session directory")
    parser.add_argument("--recordings-root", default="recordings", help="Recordings root to pick latest session from")
    parser.add_argument("--fps", type=float, choices=[8.0, 9.0, 10.0], default=10.0, help="Playback FPS")
    parser.add_argument("--pointcloud", action="store_true", help="Render point cloud NPZ frames via Open3D")
    args = parser.parse_args()

    if args.session:
        session_dir = Path(args.session)
        if not session_dir.exists():
            raise FileNotFoundError(f"Session path not found: {session_dir}")
        layout = resolve_layout(session_dir)
    else:
        session_dir, layout = find_latest_playable_layout(args.recordings_root)

    rs_rgb_files = layout["rs_rgb_files"]
    depth_files = layout["depth_files"]
    pointcloud_files = layout["pointcloud_files"]

    if not rs_rgb_files or not depth_files:
        raise RuntimeError("No RGB/depth frame files found in this session")

    frame_count = min(len(rs_rgb_files), len(depth_files))

    webcam_mode = layout["webcam_mode"]
    webcam_files = layout["webcam_files"]
    rs_video_path = layout["realsense_video"]
    rs_video_cap = None
    webcam_cap = None

    if rs_video_path:
        rs_video_cap = cv2.VideoCapture(rs_video_path)
        if not rs_video_cap.isOpened():
            print("Warning: RealSense video could not be opened, falling back to image sequence")
            rs_video_cap = None

    if webcam_mode == "video":
        webcam_cap = cv2.VideoCapture(layout["webcam_video"])
        if not webcam_cap.isOpened():
            print("Warning: webcam video could not be opened")
            webcam_mode = "none"

    if webcam_mode == "images" and not webcam_files:
        webcam_mode = "none"

    o3d_mod, vis, pcd = create_open3d_visualizer(args.pointcloud)

    if rs_video_cap is not None:
        rs_video_fps = rs_video_cap.get(cv2.CAP_PROP_FPS)
        playback_fps = rs_video_fps if rs_video_fps > 0 else args.fps
    else:
        playback_fps = args.fps

    delay_ms = max(1, int(1000.0 / max(1e-6, playback_fps)))
    paused = False
    index = 0

    depth_indices = [stem_index(path, i) for i, path in enumerate(depth_files)]
    pointcloud_indices = [stem_index(path, i) for i, path in enumerate(pointcloud_files)]

    print(f"Viewing session: {session_dir}")
    print("Controls: q=quit, space=pause/resume, n=next frame (when paused)")

    try:
        while True:
            if not paused:
                if rs_video_cap is not None:
                    ok_rs, rs_rgb = rs_video_cap.read()
                    if not ok_rs:
                        break
                else:
                    if index >= frame_count:
                        break
                    rs_rgb = cv2.imread(rs_rgb_files[index], cv2.IMREAD_COLOR)

                if rs_rgb is None:
                    print(f"Warning: missing RealSense RGB frame at index {index}, skipping")
                    index += 1
                    continue

                if rs_video_cap is not None:
                    current_rs_frame = max(0, int(rs_video_cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1)
                    depth_pos = bisect.bisect_right(depth_indices, current_rs_frame) - 1
                    depth_pos = max(0, min(depth_pos, len(depth_files) - 1))
                    depth = np.load(depth_files[depth_pos])
                    pointcloud_pos = bisect.bisect_right(pointcloud_indices, current_rs_frame) - 1
                    pointcloud_pos = max(0, min(pointcloud_pos, len(pointcloud_files) - 1))
                else:
                    depth = np.load(depth_files[index])
                    pointcloud_pos = index

                if webcam_mode == "video":
                    ok, webcam_rgb = webcam_cap.read()
                    if not ok:
                        webcam_rgb = np.zeros_like(rs_rgb)
                        cv2.putText(
                            webcam_rgb,
                            "Webcam stream ended",
                            (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1.0,
                            (0, 0, 255),
                            2,
                        )
                elif webcam_mode == "images":
                    if index < len(webcam_files):
                        webcam_rgb = cv2.imread(webcam_files[index], cv2.IMREAD_COLOR)
                        if webcam_rgb is None:
                            webcam_rgb = np.zeros_like(rs_rgb)
                    else:
                        webcam_rgb = np.zeros_like(rs_rgb)
                else:
                    webcam_rgb = np.zeros_like(rs_rgb)
                    cv2.putText(
                        webcam_rgb,
                        "No webcam source in session",
                        (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.0,
                        (0, 0, 255),
                        2,
                    )

                depth_vis = depth_to_colormap(depth)

                cv2.imshow("RealSense RGB", rs_rgb)
                cv2.imshow("Webcam RGB", webcam_rgb)
                cv2.imshow("Depth Colormap", depth_vis)

                if vis is not None:
                    pointcloud_path = pointcloud_files[pointcloud_pos] if pointcloud_files else ""
                    update_open3d(o3d_mod, vis, pcd, pointcloud_path)

                index += 1

            key = cv2.waitKey(delay_ms if not paused else 50) & 0xFF
            if key == ord("q"):
                break
            if key == ord(" "):
                paused = not paused
            if paused and key == ord("n"):
                index = min(index + 1, frame_count - 1)

    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        if rs_video_cap is not None:
            rs_video_cap.release()
        if webcam_cap is not None:
            webcam_cap.release()
        cv2.destroyAllWindows()
        if vis is not None:
            vis.destroy_window()


if __name__ == "__main__":
    main()
