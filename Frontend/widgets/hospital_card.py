from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QStyle, QVBoxLayout


class HospitalCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("panel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        title = QLabel("Hospital / Institute")
        title.setObjectName("sectionTitle")

        icon_label = QLabel()
        icon_label.setObjectName("hospitalIcon")
        icon = self.style().standardIcon(QStyle.SP_ComputerIcon)
        icon_label.setPixmap(icon.pixmap(56, 56))
        icon_label.setAlignment(Qt.AlignCenter)

        name_label = QLabel("Indian Institute of Science")
        name_label.setObjectName("profileValue")
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setWordWrap(True)

        layout.addWidget(title)
        layout.addSpacing(4)
        layout.addWidget(icon_label)
        layout.addWidget(name_label)
        layout.addStretch(1)
