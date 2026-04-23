from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from Frontend.widgets.patient_table import PatientTable
from Frontend.widgets.search_bar import SearchBar


class PatientsPage(QWidget):
    addPatientRequested = Signal()
    patientSelected = Signal(dict)

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        top_bar = QFrame()
        top_bar.setObjectName("patientsDirectoryHeader")
        top_layout = QVBoxLayout(top_bar)
        top_layout.setContentsMargins(12, 10, 12, 10)
        top_layout.setSpacing(6)

        title = QLabel("Patient Directory")
        title.setObjectName("patientsDirectoryTitle")
        subtitle = QLabel("Search and review registered patient records quickly.")
        subtitle.setObjectName("patientsDirectorySubtitle")
        top_layout.addWidget(title)
        top_layout.addWidget(subtitle)

        top_row = QHBoxLayout()
        top_row.setSpacing(8)
        self.search_bar = SearchBar()
        self.search_bar.setPlaceholderText("Search by name, UHID or GMA UHID")

        self.sort_combo = QComboBox()
        self.sort_combo.setObjectName("compactInput")
        self.sort_combo.addItems(
            [
                "Name (A-Z)",
                "Name (Z-A)",
                "Newest to Oldest",
                "Oldest to Newest",
                "UHID",
                "GMA UHID",
            ]
        )
        self.sort_combo.setVisible(False)

        self.add_button = QPushButton("Add New Patient")
        self.add_button.setObjectName("primaryButton")
        self.add_button.clicked.connect(self.addPatientRequested.emit)
        self.add_button.setVisible(False)

        top_row.addWidget(self.search_bar, 1)
        top_layout.addLayout(top_row)

        chips_row = QHBoxLayout()
        chips_row.setSpacing(6)
        self.sort_chips = {}
        chip_map = [
            ("UHID", "UHID"),
            ("GMA UHID", "GMA UHID"),
            ("Name A-Z", "Name (A-Z)"),
            ("Name Z-A", "Name (Z-A)"),
            ("Newest", "Newest to Oldest"),
        ]
        for label, mode in chip_map:
            chip = QPushButton(label)
            chip.setObjectName("sortChip")
            chip.setCheckable(True)
            chip.clicked.connect(lambda _checked=False, m=mode: self._set_sort_mode(m))
            self.sort_chips[mode] = chip
            chips_row.addWidget(chip)
        chips_row.addStretch(1)
        top_layout.addLayout(chips_row)

        self._set_sort_mode("Name (A-Z)")

        table_panel = QFrame()
        table_panel.setObjectName("patientsListPanel")
        table_layout = QVBoxLayout(table_panel)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)

        self.patient_table = PatientTable()
        self.patient_table.cellClicked.connect(self._on_row_clicked)
        table_layout.addWidget(self.patient_table)

        layout.addWidget(top_bar)
        layout.addWidget(table_panel, 1)

        self.fab_button = QPushButton("+")
        self.fab_button.setObjectName("patientsFab")
        self.fab_button.clicked.connect(self.addPatientRequested.emit)
        fab_row = QHBoxLayout()
        fab_row.setContentsMargins(0, 0, 2, 2)
        fab_row.addStretch(1)
        fab_row.addWidget(self.fab_button)
        layout.addLayout(fab_row)

    def _set_sort_mode(self, mode):
        for sort_mode, chip in self.sort_chips.items():
            chip.setChecked(sort_mode == mode)
        self.sort_combo.setCurrentText(mode)

    def _on_row_clicked(self, row, _column):
        patient = self.patient_table.get_row_data(row)
        if patient is not None:
            self.patientSelected.emit(patient)
