import argparse
from pathlib import Path

import cv2


def _latest_session(root: Path) -> Path:
    sessions = sorted((path for path in root.glob("session_*") if path.is_dir()), key=lambda path: path.stat().st_mtime)
    if not sessions:
        raise RuntimeError(f"No session folders found in {root}")
    return sessions[-1]


def _pick_video(session_dir: Path) -> Path:
    for stem in ("realsense", "color_output"):
        for ext in (".avi", ".mp4", ".mov", ".mkv"):
            candidate = session_dir / f"{stem}{ext}"
            if candidate.exists():
                return candidate
    raise RuntimeError(f"No recorded color video found in {session_dir}")


def _resolve_session_path(value: str | None) -> Path:
    root = Path("recordings")
    if value:
        candidate = Path(value)
        if candidate.is_file():
            return candidate
        if candidate.is_dir():
            return _pick_video(candidate)
        raise RuntimeError(f"Session path does not exist: {value}")

    if not root.exists():
        raise RuntimeError("No recordings directory found")

    return _pick_video(_latest_session(root))


def main() -> int:
    parser = argparse.ArgumentParser(description="Play a recorded RealSense color session")
    parser.add_argument("--session", help="Session folder or video path", default=None)
    parser.add_argument("--fps", type=float, default=30.0, help="Fallback playback FPS")
    args = parser.parse_args()

    video_path = _resolve_session_path(args.session)
    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise RuntimeError(f"Unable to open video: {video_path}")

    fps = capture.get(cv2.CAP_PROP_FPS) or args.fps
    delay_ms = max(1, int(1000.0 / max(1.0, fps)))

    print(f"Playing {video_path}")
    print(f"FPS={fps:.2f}")

    paused = False
    while True:
        if not paused:
            ok, frame = capture.read()
            if not ok:
                break
            cv2.imshow("RealSense Color", frame)

        key = cv2.waitKey(delay_ms) & 0xFF
        if key in (ord("q"), 27):
            break
        if key == ord(" "):
            paused = not paused

    capture.release()
    cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
