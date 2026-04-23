from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget

from Frontend.widgets.upload_card import UploadCard


class UploadsPage(QWidget):
    patientRequested = Signal(str)

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        top_bar = QFrame()
        top_bar.setObjectName("uploadsTopBar")
        top_layout = QVBoxLayout(top_bar)
        top_layout.setContentsMargins(12, 6, 12, 6)
        top_layout.setSpacing(4)

        title = QLabel("Upload Queue")
        title.setObjectName("uploadsQueueTitle")
        top_layout.addWidget(title)

        tabs = QHBoxLayout()
        tabs.setSpacing(6)
        self.pending_tab = QPushButton("Pending")
        self.uploaded_tab = QPushButton("Uploaded")
        self.rejected_tab = QPushButton("Rejected")
        self.pending_tab.setProperty("tabVariant", "pending")
        self.uploaded_tab.setProperty("tabVariant", "uploaded")
        self.rejected_tab.setProperty("tabVariant", "rejected")
        for btn in [self.pending_tab, self.uploaded_tab, self.rejected_tab]:
            btn.setCheckable(True)
            btn.setObjectName("uploadTab")
            tabs.addWidget(btn)
        tabs.addStretch(1)
        top_layout.addLayout(tabs)

        list_panel = QFrame()
        list_panel.setObjectName("uploadsListPanel")
        list_layout = QVBoxLayout(list_panel)
        list_layout.setContentsMargins(8, 8, 8, 8)
        list_layout.setSpacing(0)

        self.pending_container, self.pending_layout, self.pending_scroll = self._create_list_container()
        self.uploaded_container, self.uploaded_layout, self.uploaded_scroll = self._create_list_container()
        self.rejected_container, self.rejected_layout, self.rejected_scroll = self._create_list_container()

        self.pending_tab.clicked.connect(lambda: self.set_active_tab("pending"))
        self.uploaded_tab.clicked.connect(lambda: self.set_active_tab("uploaded"))
        self.rejected_tab.clicked.connect(lambda: self.set_active_tab("rejected"))

        self._counts = {"pending": 0, "uploaded": 0, "rejected": 0}

        list_layout.addWidget(self.pending_scroll)
        list_layout.addWidget(self.uploaded_scroll)
        list_layout.addWidget(self.rejected_scroll)

        layout.addWidget(top_bar)
        layout.addWidget(list_panel, 1)

        self.set_active_tab("pending")

    def _create_list_container(self):
        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(6)
        vbox.addStretch(1)

        scroll = QScrollArea()
        scroll.setObjectName("uploadsScroll")
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)
        scroll.setFrameShape(QScrollArea.NoFrame)
        return container, vbox, scroll

    def _clear_layout(self, layout):
        while layout.count() > 1:
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _set_cards(self, layout, uploads):
        self._clear_layout(layout)
        for item in uploads:
            card = UploadCard(
                patient_name=item.get("patient_name", "--"),
                uhid=item.get("uhid", "--"),
                duration=item.get("duration", "00:00:00"),
                file_size=item.get("file_size", "0 MB"),
                timestamp=item.get("timestamp", "--"),
                status=item.get("status", "pending"),
            )
            card.clicked.connect(self.patientRequested.emit)
            layout.insertWidget(layout.count() - 1, card)

    def set_uploads(self, pending, uploaded, rejected):
        self._set_cards(self.pending_layout, pending)
        self._set_cards(self.uploaded_layout, uploaded)
        self._set_cards(self.rejected_layout, rejected)
        self._counts = {
            "pending": len(pending),
            "uploaded": len(uploaded),
            "rejected": len(rejected),
        }
        active = "pending"
        if self.uploaded_tab.isChecked():
            active = "uploaded"
        elif self.rejected_tab.isChecked():
            active = "rejected"
        self._update_tab_labels(active)

    def _update_tab_labels(self, active_status):
        self.pending_tab.setText(f"Pending ({self._counts['pending']})" if active_status == "pending" else "Pending")
        self.uploaded_tab.setText(f"Uploaded ({self._counts['uploaded']})" if active_status == "uploaded" else "Uploaded")
        self.rejected_tab.setText(f"Rejected ({self._counts['rejected']})" if active_status == "rejected" else "Rejected")

    def set_active_tab(self, status):
        states = {
            "pending": self.pending_tab,
            "uploaded": self.uploaded_tab,
            "rejected": self.rejected_tab,
        }
        for key, btn in states.items():
            btn.setChecked(key == status)

        self.pending_scroll.setVisible(status == "pending")
        self.uploaded_scroll.setVisible(status == "uploaded")
        self.rejected_scroll.setVisible(status == "rejected")
        self._update_tab_labels(status)
