from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QMessageBox
from PySide6.QtCore import QTimer, Signal
import threading

from recorder import Recorder


class MainWindow(QWidget):
    recording_started = Signal()
    recording_start_failed = Signal(str)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Camera Recorder")
        self.setMinimumSize(300, 200)

        self.controller = Recorder()

        layout = QVBoxLayout()

        self.start_btn = QPushButton("Start Recording")
        self.stop_btn = QPushButton("Stop Recording")
        self.stop_btn.setEnabled(False)

        self.timer_label = QLabel("00:00")
        self.timer_label.setStyleSheet("font-size: 24px; font-weight: bold;")

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.seconds = 0

        layout.addWidget(self.timer_label)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)

        self.setLayout(layout)

        self.start_btn.clicked.connect(self.start_recording)
        self.stop_btn.clicked.connect(self.stop_recording)

        self.start_thread = None

        self.recording_started.connect(self._handle_started)
        self.recording_start_failed.connect(self._handle_start_error)

    def _handle_started(self):
        self.seconds = 0
        self.timer.start(1000)
        self.stop_btn.setEnabled(True)

    def _handle_start_error(self, message):
        self.timer.stop()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        QMessageBox.critical(self, "Error", message)

    def start_recording(self):
        if self.start_thread and self.start_thread.is_alive():
            return

        # Wait for successful backend start before showing recording time.
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)

        def _start_worker():
            try:
                self.controller.start()
                self.recording_started.emit()
            except Exception as e:
                self.recording_start_failed.emit(str(e))

        self.start_thread = threading.Thread(target=_start_worker, daemon=True)
        self.start_thread.start()

    def stop_recording(self):
        try:
            self.controller.stop()

            self.timer.stop()
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)

            if self.controller.last_error is not None:
                QMessageBox.warning(self, "Recording Warning", f"Capture stopped due to error:\n{self.controller.last_error}")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def update_timer(self):
        self.seconds += 1
        mins = self.seconds // 60
        secs = self.seconds % 60
        self.timer_label.setText(f"{mins:02}:{secs:02}")


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
