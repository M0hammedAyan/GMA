from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget


class PatientRowCard(QFrame):
    clicked = Signal(int)
    recordClicked = Signal(int)
    uploadClicked = Signal(int)

    def __init__(self, row_index, row_data):
        super().__init__()
        self._row_index = row_index
        self.setObjectName("patientListCard")
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_Hover, True)
        self.setMouseTracking(True)
        self._apply_shadow(8, 1, 35)

        root = QHBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(10)

        name = str(row_data.get("Name", "")).strip()
        avatar_text = name[0].upper() if name else "P"

        avatar = QLabel(avatar_text)
        avatar.setObjectName("patientAvatar")
        avatar.setFixedSize(36, 36)
        avatar.setAlignment(Qt.AlignCenter)
        root.addWidget(avatar, 0, Qt.AlignTop)

        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(2)

        title = QLabel(name or "Unknown Patient")
        title.setObjectName("patientName")

        uhid = str(row_data.get("UHID", "--")).strip()
        gma = str(row_data.get("GMA", "--")).strip()
        gender = str(row_data.get("Gender", "--")).strip()
        ga = str(row_data.get("Age/Weeks", "--")).strip()
        dob = str(row_data.get("DOB", "--")).strip()

        meta_one = QLabel(f"UHID  {uhid}")
        meta_one.setObjectName("patientMeta")
        meta_two = QLabel(f"{gma}    {gender}    GA {ga}w")
        meta_two.setObjectName("patientMeta")
        meta_three = QLabel(dob)
        meta_three.setObjectName("patientMeta")

        text_col.addWidget(title)
        text_col.addWidget(meta_one)
        text_col.addWidget(meta_two)
        text_col.addWidget(meta_three)

        root.addLayout(text_col, 1)

        actions_col = QVBoxLayout()
        actions_col.setContentsMargins(6, 2, 4, 2)
        actions_col.setSpacing(8)
        actions_col.addStretch(1)

        self.record_btn = QPushButton("Record")
        self.record_btn.setObjectName("patientActionButton")
        self.record_btn.setProperty("variant", "record")
        self.record_btn.clicked.connect(lambda: self.recordClicked.emit(self._row_index))

        self.upload_btn = QPushButton("Upload")
        self.upload_btn.setObjectName("patientActionButton")
        self.upload_btn.setProperty("variant", "upload")
        self.upload_btn.clicked.connect(lambda: self.uploadClicked.emit(self._row_index))

        actions_col.addWidget(self.record_btn)
        actions_col.addWidget(self.upload_btn)
        actions_col.addStretch(1)
        root.addLayout(actions_col)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self._row_index)
        super().mousePressEvent(event)

    def _apply_shadow(self, blur, y_offset, alpha):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(blur)
        shadow.setOffset(0, y_offset)
        shadow.setColor(QColor(15, 23, 42, alpha))
        self.setGraphicsEffect(shadow)

    def enterEvent(self, event):
        self._apply_shadow(18, 3, 80)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._apply_shadow(8, 1, 35)
        super().leaveEvent(event)


class PatientTable(QWidget):
    cellClicked = Signal(int, int)
    recordRequested = Signal(int)
    uploadRequested = Signal(int)
    headers = ["UHID", "GMA", "Name", "Age/Weeks", "DOB", "Gender"]

    def __init__(self):
        super().__init__()
        self._rows = []

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.scroll = QScrollArea()
        self.scroll.setObjectName("patientsListScroll")
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)

        self.body = QWidget()
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(8)
        self.body_layout.addStretch(1)

        self.scroll.setWidget(self.body)
        root.addWidget(self.scroll)

    def set_rows(self, rows):
        self._rows = [dict(row) for row in rows]

        while self.body_layout.count() > 1:
            item = self.body_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        for row_idx, row_data in enumerate(self._rows):
            card = PatientRowCard(row_idx, row_data)
            card.clicked.connect(lambda idx=row_idx: self.cellClicked.emit(idx, 0))
            card.recordClicked.connect(lambda idx=row_idx: self.recordRequested.emit(idx))
            card.uploadClicked.connect(lambda idx=row_idx: self.uploadRequested.emit(idx))
            self.body_layout.insertWidget(self.body_layout.count() - 1, card)

    def get_row_data(self, row_index):
        if not (0 <= row_index < len(self._rows)):
            return None
        return dict(self._rows[row_index])
