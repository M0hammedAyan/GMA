from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QMessageBox
from PySide6.QtCore import QTimer

from recorder_controller import RecorderController


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Camera Recorder")
        self.setMinimumSize(300, 200)

        self.controller = RecorderController()

        self.layout = QVBoxLayout()

        # Buttons
        self.start_btn = QPushButton("Start Recording")
        self.stop_btn = QPushButton("Stop Recording")

        self.stop_btn.setEnabled(False)

        # Timer label
        self.timer_label = QLabel("00:00")
        self.timer_label.setStyleSheet("font-size: 24px; font-weight: bold;")

        # Timer logic
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.seconds = 0

        # Layout
        self.layout.addWidget(self.timer_label)
        self.layout.addWidget(self.start_btn)
        self.layout.addWidget(self.stop_btn)

        self.setLayout(self.layout)

        # Connections
        self.start_btn.clicked.connect(self.start_recording)
        self.stop_btn.clicked.connect(self.stop_recording)

    def start_recording(self):
        try:
            self.controller.start_recording()

            # Start UI timer
            self.seconds = 0
            self.timer.start(1000)  # every 1 second

            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def stop_recording(self):
        try:
            self.controller.stop_recording()

            # Stop UI timer
            self.timer.stop()

            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)

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
