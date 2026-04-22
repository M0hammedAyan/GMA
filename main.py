import sys
import traceback
import faulthandler
import argparse
import time
from pathlib import Path


def _ensure_project_root_on_path() -> None:
    # Allow `python main.py` from any working directory.
    project_root = Path(__file__).resolve().parent
    root_str = str(project_root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)


def _run_headless() -> int:
    from recorder import Recorder

    def _format_hms(total_seconds: int) -> str:
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    recorder = Recorder()
    try:
        recorder.start()
        print("Headless recording started. Press Ctrl+C to stop.")
        while True:
            time.sleep(1.0)
            elapsed = recorder.elapsed_seconds()
            print(f"\rRecording time: {_format_hms(elapsed)}", end="", flush=True)
            if recorder.last_error is not None:
                raise RuntimeError(recorder.last_error)
    except KeyboardInterrupt:
        print()
        return 0
    finally:
        print()
        recorder.stop()


def _run_single_button_gui() -> int:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget
    from recorder import Recorder

    class SingleButtonWindow(QWidget):
        def __init__(self):
            super().__init__()
            self.recorder = Recorder()
            self.is_running = False

            self.setWindowTitle("GMA Recorder")
            self.setMinimumSize(360, 180)

            layout = QVBoxLayout(self)
            layout.setAlignment(Qt.AlignCenter)

            self.status_label = QLabel("Ready")
            self.status_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(self.status_label)

            self.toggle_button = QPushButton("Start Recording")
            self.toggle_button.clicked.connect(self._toggle_recording)
            layout.addWidget(self.toggle_button)

        def _toggle_recording(self):
            if self.is_running:
                self.recorder.stop()
                self.is_running = False
                self.toggle_button.setText("Start Recording")
                self.status_label.setText("Stopped")
                return

            try:
                self.recorder.start()
            except Exception as err:
                self.status_label.setText(f"Error: {err}")
                return

            self.is_running = True
            self.toggle_button.setText("Stop Recording")
            self.status_label.setText("Recording")

        def closeEvent(self, event):
            try:
                self.recorder.stop()
            except Exception:
                pass
            super().closeEvent(event)

    app = QApplication(sys.argv)
    window = SingleButtonWindow()
    window.show()
    return app.exec()


def run(argv=None) -> int:
    _ensure_project_root_on_path()
    faulthandler.enable(all_threads=True)

    parser = argparse.ArgumentParser(description="GMA recording application")
    parser.add_argument("--button-gui", action="store_true", help="Run a minimal single-button Qt launcher")
    args = parser.parse_args(argv)

    try:
        if args.button_gui:
            return _run_single_button_gui()
        return _run_headless()
    except Exception as err:
        mode = "button-gui" if args.button_gui else "headless"
        print(f"Fatal {mode} error: {err}", file=sys.stderr)
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(run())
