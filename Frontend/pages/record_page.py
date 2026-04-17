# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportMissingParameterType=false, reportGeneralTypeIssues=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class RecordPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        top_row = QHBoxLayout()
        top_row.setSpacing(8)
        self.back_button = QPushButton("Back to Patients")
        self.back_button.setObjectName("backButton")
        top_row.addWidget(self.back_button, 0, Qt.AlignLeft)
        top_row.addStretch(1)
        layout.addLayout(top_row)

        shell = QFrame()
        shell.setObjectName("recordShell")
        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(14, 14, 14, 14)
        shell_layout.setSpacing(12)

        content_panel = QFrame()
        content_panel.setObjectName("recordLeftPanel")
        content_layout = QVBoxLayout(content_panel)
        content_layout.setContentsMargins(12, 12, 12, 12)
        content_layout.setSpacing(8)

        details_title = QLabel("Patient Details")
        details_title.setObjectName("sectionTitle")
        content_layout.addWidget(details_title)

        self.details_container = QWidget()
        self.details_layout = QVBoxLayout(self.details_container)
        self.details_layout.setContentsMargins(0, 0, 0, 0)
        self.details_layout.setSpacing(6)
        content_layout.addWidget(self.details_container)

        history_title = QLabel("Recording History")
        history_title.setObjectName("sectionTitle")
        content_layout.addWidget(history_title)

        self.history_list = QListWidget()
        self.history_list.setObjectName("patientHistoryList")
        self.history_list.setMinimumHeight(180)
        content_layout.addWidget(self.history_list)

        content_scroll = QScrollArea()
        content_scroll.setObjectName("recordContentScroll")
        content_scroll.setWidgetResizable(True)
        content_scroll.setFrameShape(QScrollArea.NoFrame)
        content_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content_scroll.setWidget(content_panel)
        self.content_scroll = content_scroll

        shell_layout.addWidget(content_scroll, 1)

        self.preview_card = QFrame()
        self.preview_card.setObjectName("recordPreviewCard")
        preview_layout = QVBoxLayout(self.preview_card)
        preview_layout.setContentsMargins(12, 12, 12, 12)
        preview_layout.setSpacing(10)

        chip_row = QHBoxLayout()
        chip_row.setSpacing(8)
        self.gps_chip = QLabel("GPS: Awaiting coordinates")
        self.gps_chip.setObjectName("previewChip")
        self.timestamp_chip = QLabel("Timestamp: Not recording yet")
        self.timestamp_chip.setObjectName("previewChip")
        chip_row.addWidget(self.gps_chip)
        chip_row.addWidget(self.timestamp_chip)
        self.preview_mode_combo = QComboBox()
        self.preview_mode_combo.addItems(
            [
                "Both Cameras",
                "RealSense Depth (Color) + Color",
                "RealSense Depth (Color) + Webcam",
            ]
        )
        self.preview_mode_combo.setObjectName("filterChip")
        chip_row.addWidget(self.preview_mode_combo)
        chip_row.addStretch(1)
        preview_layout.addLayout(chip_row)

        labels_row = QHBoxLayout()
        labels_row.setSpacing(8)
        self.preview_left_title = QLabel("RealSense")
        self.preview_left_title.setObjectName("sectionTitle")
        self.preview_right_title = QLabel("Webcam")
        self.preview_right_title.setObjectName("sectionTitle")
        labels_row.addWidget(self.preview_left_title)
        labels_row.addStretch(1)
        labels_row.addWidget(self.preview_right_title)
        preview_layout.addLayout(labels_row)

        previews_row = QHBoxLayout()
        previews_row.setSpacing(8)
        self.preview_left_surface = QLabel("Live camera feed unavailable")
        self.preview_left_surface.setObjectName("previewSurface")
        self.preview_left_surface.setAlignment(Qt.AlignCenter)
        self.preview_left_surface.setMinimumHeight(320)

        self.preview_right_surface = QLabel("Live camera feed unavailable")
        self.preview_right_surface.setObjectName("previewSurface")
        self.preview_right_surface.setAlignment(Qt.AlignCenter)
        self.preview_right_surface.setMinimumHeight(320)

        previews_row.addWidget(self.preview_left_surface, 1)
        previews_row.addWidget(self.preview_right_surface, 1)
        preview_layout.addLayout(previews_row, 1)

        status_row = QHBoxLayout()
        status_row.setSpacing(8)
        self.standby_chip = QLabel("STANDBY")
        self.standby_chip.setObjectName("previewStatusChip")
        self.lighting_chip = QLabel("Lighting OK")
        self.lighting_chip.setObjectName("previewStatusChip")
        status_row.addWidget(self.standby_chip)
        status_row.addStretch(1)
        status_row.addWidget(self.lighting_chip)
        preview_layout.addLayout(status_row)

        shell_layout.addWidget(self.preview_card, 1)

        record_row = QHBoxLayout()
        record_row.setSpacing(10)
        self.action_btn = QPushButton("Start Recording")
        self.action_btn.setObjectName("primaryButton")
        self.upload_btn = QPushButton("Upload")
        self.upload_btn.setObjectName("secondaryButton")
        self.timer_label = QLabel("00:00:00")
        self.timer_label.setObjectName("timer")
        record_row.addWidget(self.upload_btn)
        record_row.addWidget(self.action_btn, 1)
        record_row.addWidget(self.timer_label, 0, Qt.AlignVCenter)
        shell_layout.addLayout(record_row)

        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("stateBadge")

        layout.addWidget(shell, 1)
        layout.addWidget(self.status_label)

        self.set_upload_history([])
        self.set_recording_mode(False)

    def _field_label(self, text):
        label = QLabel(text)
        label.setObjectName("recordField")
        label.setMinimumHeight(42)
        label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        return label

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _missing(self, value):
        text = str(value or "").strip()
        return text == "" or text == "--"

    def set_patient(self, patient):
        self._clear_layout(self.details_layout)

        detail_fields = [
            ("Patient Name", patient.get("Name", "")),
            ("Gender", patient.get("Gender", "")),
            ("Gestational Age (weeks)", patient.get("Age/Weeks", "")),
            ("Date of Birth", patient.get("DOB", "")),
            ("Hospital UHID", patient.get("UHID", "")),
            ("GMA UHID", patient.get("GMA", "")),
            ("Parent/Guardian Name", patient.get("Parent/Guardian Name", "")),
            ("Parent/Guardian Phone", patient.get("Parent/Guardian Phone", "")),
            ("Address", patient.get("Address", "")),
            ("Location", patient.get("Location", "")),
        ]

        visible_count = 0
        for label_text, value in detail_fields:
            if self._missing(value):
                continue
            field = self._field_label(f"{label_text}: {value}")
            self.details_layout.addWidget(field)
            visible_count += 1

        if visible_count == 0:
            self.details_layout.addWidget(self._field_label("No patient details available"))

        self.details_layout.addStretch(1)

    def set_upload_history(self, history_entries):
        self.history_list.clear()
        if not history_entries:
            self.history_list.addItem(QListWidgetItem("No recordings yet for this patient"))
            return

        for entry in history_entries:
            status = str(entry.get("status", "pending")).capitalize()
            timestamp = str(entry.get("timestamp", "--"))
            duration = str(entry.get("duration", "00:00:00"))
            size = str(entry.get("file_size", "0 MB"))
            self.history_list.addItem(QListWidgetItem(f"{timestamp} | {status} | {duration} | {size}"))

    def set_recording_mode(self, recording):
        self.content_scroll.setVisible(not recording)
        self.preview_card.setVisible(recording)
        self.upload_btn.setVisible(not recording)

        if recording:
            self.standby_chip.setText("RECORDING")
            self.standby_chip.setProperty("state", "recording")
            self.timestamp_chip.setText("Timestamp: Recording started")
        else:
            self.standby_chip.setText("STANDBY")
            self.standby_chip.setProperty("state", "standby")
            self.timestamp_chip.setText("Timestamp: Not recording yet")

        self.standby_chip.style().unpolish(self.standby_chip)
        self.standby_chip.style().polish(self.standby_chip)

    def set_preview_timer(self, timer_text):
        self.timestamp_chip.setText(f"Timestamp: Recording {timer_text}")

    def set_preview_error(self, message):
        self.standby_chip.setText("DEVICE MISSING")
        self.standby_chip.setProperty("state", "error")
        self.timestamp_chip.setText(f"Timestamp: {message}")
        self.standby_chip.style().unpolish(self.standby_chip)
        self.standby_chip.style().polish(self.standby_chip)
