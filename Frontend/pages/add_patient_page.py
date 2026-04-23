from datetime import date

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class AddPatientPage(QWidget):
    def __init__(self):
        super().__init__()
        self._seed = 1003

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        top_bar = QFrame()
        top_bar.setObjectName("addPatientTopBar")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(12, 10, 12, 10)
        top_layout.setSpacing(8)

        title = QLabel("Add New Patient")
        title.setObjectName("sectionTitle")
        top_layout.addWidget(title)
        top_layout.addStretch(1)
        root.addWidget(top_bar)

        body = QHBoxLayout()
        body.setSpacing(6)

        form_card = QFrame()
        form_card.setObjectName("addPatientFormPanel")
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(12, 12, 12, 12)
        form_layout.setSpacing(10)

        form = QFormLayout()
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(10)

        self.name_input = QLineEdit()
        self.dob_input = QDateEdit()
        self.dob_input.setCalendarPopup(True)
        self.dob_input.setMinimumDate(QDate(1900, 1, 1))
        self.dob_input.setSpecialValueText("Select DOB")
        self.dob_input.setDate(QDate(1900, 1, 1))
        self.age_input = QSpinBox()
        self.age_input.setRange(0, 50)
        self.age_input.setSpecialValueText("Enter weeks")
        self.age_input.setValue(0)
        self.uhid_input = QLineEdit()
        self.uhid_input.setReadOnly(True)
        self.uhid_input.setPlaceholderText("Auto-generated on save")
        self.gma_uhid_input = QLineEdit()
        self.gma_uhid_input.setReadOnly(True)
        self.gma_uhid_input.setPlaceholderText("Auto-generated on save")
        self.gender_input = QComboBox()
        self.gender_input.addItems(["Select Gender", "Male", "Female", "Other"])

        for field in [self.name_input, self.dob_input, self.age_input, self.uhid_input, self.gma_uhid_input, self.gender_input]:
            field.setObjectName("compactInput")

        def _label(text):
            lbl = QLabel(text)
            lbl.setObjectName("formLabel")
            return lbl

        form.addRow(_label("Patient Name"), self.name_input)
        form.addRow(_label("DOB"), self.dob_input)
        form.addRow(_label("Gestational Age (weeks)"), self.age_input)
        form.addRow(_label("Hospital UHID"), self.uhid_input)
        form.addRow(_label("GMA UHID"), self.gma_uhid_input)
        form.addRow(_label("Gender"), self.gender_input)

        form_layout.addLayout(form)

        body.addWidget(form_card, 1)

        root.addLayout(body, 1)

        actions = QHBoxLayout()
        actions.setSpacing(6)
        actions.addStretch(1)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("secondaryButton")
        self.save_btn = QPushButton("Save Patient")
        self.save_btn.setObjectName("primaryButton")
        self.save_btn.setFixedWidth(140)
        actions.addWidget(self.cancel_btn, 0, Qt.AlignVCenter)
        actions.addWidget(self.save_btn, 0, Qt.AlignVCenter)
        root.addLayout(actions)

        self.load_new_patient()

    def generate_uhid(self):
        self._seed += 1
        return f"U{self._seed}"

    def generate_gma_uhid(self):
        today = date.today().strftime("%m%d")
        return f"GMA{today}{self._seed}"

    def load_new_patient(self):
        self.name_input.clear()
        self.dob_input.setDate(QDate(1900, 1, 1))
        self.age_input.setValue(0)
        self.gender_input.setCurrentIndex(0)
        self.uhid_input.setText(self.generate_uhid())
        self.gma_uhid_input.setText(self.generate_gma_uhid())

    def get_patient(self):
        if not self.uhid_input.text().strip():
            self.uhid_input.setText(self.generate_uhid())
        if not self.gma_uhid_input.text().strip():
            self.gma_uhid_input.setText(self.generate_gma_uhid())

        dob_value = self.dob_input.date()
        dob_text = dob_value.toString("yyyy-MM-dd")
        if dob_value == QDate(1900, 1, 1):
            dob_text = date.today().strftime("%Y-%m-%d")

        age_value = self.age_input.value()
        age_text = str(age_value) if age_value > 0 else ""

        gender_text = self.gender_input.currentText()
        if gender_text == "Select Gender":
            gender_text = ""

        return {
            "UHID": self.uhid_input.text().strip(),
            "GMA": self.gma_uhid_input.text().strip(),
            "Name": self.name_input.text().strip() or "Unknown",
            "Age/Weeks": age_text,
            "DOB": dob_text,
            "Gender": gender_text,
            "Status": "Pending",
        }
