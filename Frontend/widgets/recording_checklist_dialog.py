from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout


class RecordingChecklistDialog(QDialog):
    SKIPPED = 2

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Recording Checklist")
        self.setModal(True)
        self.resize(680, 620)

        assets_dir = Path(__file__).resolve().parents[1] / "assets" / "checklist"
        self.steps = [
            {
                "title": "Spine position",
                "subtitle": "Spine Position",
                "description": "Baby should not be on one side.",
                "image": assets_dir / "spine position.jpeg",
            },
            {
                "title": "Ensure the infant is awake",
                "subtitle": "Infant Awake",
                "description": "Ensure the infant is awake before recording.",
                "image": assets_dir / "infant awake.jpeg",
            },
            {
                "title": "All joints should be visible",
                "subtitle": "All Joints Visible",
                "description": "Keep the baby fully visible with all joints in frame.",
                "image": assets_dir / "visible joints.jpeg",
            },
            {
                "title": "Infant should not be sleeping",
                "subtitle": "No Sleeping",
                "description": "Do not record while the infant is sleeping.",
                "image": assets_dir / "should not be sleeping.jpeg",
            },
            {
                "title": "Continuously crying",
                "subtitle": "Continuous Crying",
                "description": "Pause and settle the infant if crying continues.",
                "image": assets_dir / "continuously crying.jpeg",
            },
        ]
        self.current_index = 0

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        top = QHBoxLayout()
        top.setSpacing(8)
        self.skip_btn = QPushButton("Skip")
        self.skip_btn.clicked.connect(self._on_skip)
        top.addStretch(1)
        top.addWidget(self.skip_btn)
        root.addLayout(top)

        card = QFrame()
        card.setObjectName("checklistCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 14, 14, 14)
        card_layout.setSpacing(10)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(500)
        self.image_label.setObjectName("checklistImage")
        card_layout.addWidget(self.image_label)

        root.addWidget(card, 1)

        self.next_btn = QPushButton("Next")
        self.next_btn.setObjectName("primaryButton")
        self.next_btn.setMinimumHeight(44)
        self.next_btn.clicked.connect(self._on_next)
        root.addWidget(self.next_btn)

        self.setStyleSheet(
            """
            QDialog { background: #F8FCFF; }
            QFrame#checklistCard {
                background: #FFFFFF;
                border: 1px solid #BFDBFE;
                border-radius: 16px;
            }
            QLabel#checklistTitle {
                font-size: 24px;
                font-weight: 700;
                color: #0F172A;
            }
            QLabel#checklistImage {
                background: #EFF6FF;
                border: 1px solid #BFDBFE;
                border-radius: 14px;
            }
            QPushButton {
                font-size: 18px;
                font-weight: 700;
                border-radius: 12px;
                padding: 8px 14px;
            }
            QPushButton#primaryButton {
                background: #2563EB;
                border: 1px solid #2563EB;
                color: #FFFFFF;
            }
            """
        )

        self._render_step()

    def _on_skip(self):
        self.done(self.SKIPPED)

    def _on_next(self):
        if self.current_index >= len(self.steps) - 1:
            self.accept()
            return
        self.current_index += 1
        self._render_step()

    def _render_step(self):
        step = self.steps[self.current_index]

        pixmap = QPixmap(str(step["image"]))
        if pixmap.isNull():
            self.image_label.setText("Checklist image not found")
        else:
            self.image_label.setPixmap(
                pixmap.scaled(
                    620,
                    480,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )

        if self.current_index == len(self.steps) - 1:
            self.next_btn.setText("I Understand & Start")
            self.next_btn.setStyleSheet("background: #1D4ED8; border: 1px solid #1D4ED8; color: #FFFFFF;")
        else:
            self.next_btn.setText("Next")
            self.next_btn.setStyleSheet("")
