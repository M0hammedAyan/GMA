from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QVBoxLayout, QWidget


class UploadCard(QWidget):
    clicked = Signal(str)

    def __init__(self, patient_name, uhid, duration, file_size, timestamp, status):
        super().__init__()
        self._uhid = str(uhid)
        self.setAttribute(Qt.WA_Hover, True)
        self.setMouseTracking(True)

        self.card = QFrame()
        self.card.setObjectName("uploadCard")
        self.card.setCursor(Qt.PointingHandCursor)
        self._apply_shadow(8, 1, 35)
        status_key = status.lower()
        if status_key == "pending":
            self.card.setProperty("status", "pending")
        elif status_key in {"successful", "uploaded", "uploading"}:
            self.card.setProperty("status", "uploading")
        else:
            self.card.setProperty("status", "rejected")

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(10, 6, 10, 6)
        card_layout.setSpacing(0)

        row1 = QHBoxLayout()
        row1.setContentsMargins(0, 0, 0, 0)
        row1.setSpacing(4)
        name_label = QLabel(patient_name)
        name_label.setObjectName("uploadPatientName")
        name_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        status_label = QLabel(status.capitalize())
        if status_key == "pending":
            status_label.setObjectName("uploadBadgePending")
        elif status_key == "uploading":
            status_label.setObjectName("uploadBadgeUploaded")
            status_label.setText("Uploading")
        elif status_key == "successful" or status_key == "uploaded":
            status_label.setObjectName("uploadBadgeUploaded")
            status_label.setText("Uploaded")
        else:
            status_label.setObjectName("uploadBadgeRejected")
            status_label.setText("Rejected")
        status_label.setAlignment(Qt.AlignCenter)

        row1.addWidget(name_label)
        row1.addStretch(1)
        row1.addWidget(status_label, 0, Qt.AlignVCenter)

        row2 = QHBoxLayout()
        row2.setContentsMargins(0, 0, 0, 0)
        row2.setSpacing(4)
        uhid_label = QLabel(f"UHID: {uhid}")
        uhid_label.setObjectName("uploadMeta")
        uhid_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        row2.addWidget(uhid_label)

        row3 = QHBoxLayout()
        row3.setContentsMargins(0, 0, 0, 0)
        row3.setSpacing(4)
        duration_label = QLabel(duration)
        duration_label.setObjectName("uploadMeta")
        duration_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        size_label = QLabel(file_size)
        size_label.setObjectName("uploadMeta")
        size_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        row3.addWidget(duration_label)
        row3.addStretch(1)
        row3.addWidget(size_label)

        row4 = QHBoxLayout()
        row4.setContentsMargins(0, 0, 0, 0)
        row4.setSpacing(4)
        ts_label = QLabel(timestamp)
        ts_label.setObjectName("uploadMeta")
        ts_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        row4.addWidget(ts_label)

        card_layout.addLayout(row1)
        card_layout.addLayout(row2)
        card_layout.addLayout(row3)
        card_layout.addLayout(row4)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(self.card)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self._uhid)
        super().mousePressEvent(event)

    def _apply_shadow(self, blur, y_offset, alpha):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(blur)
        shadow.setOffset(0, y_offset)
        shadow.setColor(QColor(15, 23, 42, alpha))
        self.card.setGraphicsEffect(shadow)

    def enterEvent(self, event):
        self._apply_shadow(18, 3, 80)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._apply_shadow(8, 1, 35)
        super().leaveEvent(event)
