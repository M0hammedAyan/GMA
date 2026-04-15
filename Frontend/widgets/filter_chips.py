from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QWidget


class FilterChips(QWidget):
    filterChanged = Signal(str)

    def __init__(self):
        super().__init__()
        self._buttons = {}

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        for label in ["All", "Pending", "Approved", "Rejected"]:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setObjectName("filterChip")
            btn.clicked.connect(lambda _checked=False, value=label: self.set_active(value))
            layout.addWidget(btn)
            self._buttons[label] = btn

        layout.addStretch(1)
        self.set_active("All")

    def set_active(self, label):
        for key, btn in self._buttons.items():
            btn.setChecked(key == label)
        self.filterChanged.emit(label)
