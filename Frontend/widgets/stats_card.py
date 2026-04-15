from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class StatsCard(QFrame):
    clicked = Signal()

    def __init__(self, title, value="0", variant="default"):
        super().__init__()
        self.setObjectName("statsCard")
        self.setProperty("variant", variant)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(128)
        self.setMaximumHeight(156)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(2)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("statsTitle")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.value_label = QLabel(str(value))
        self.value_label.setObjectName("statsValue")
        self.value_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)

    def set_value(self, value):
        self.value_label.setText(str(value))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
