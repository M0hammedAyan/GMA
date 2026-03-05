from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from recorder_controller import RecorderController

if __name__ == "__main__":
    app = QApplication([])
    
    controller = RecorderController()
    
    window = QWidget()
    layout = QVBoxLayout()
    
    start_btn = QPushButton("Start Recording")
    stop_btn = QPushButton("Stop Recording")
    
    layout.addWidget(start_btn)
    layout.addWidget(stop_btn)
    
    window.setLayout(layout)
    
    start_btn.clicked.connect(controller.start_recording)
    stop_btn.clicked.connect(controller.stop_recording)
    
    window.show()
    
    app.exec()