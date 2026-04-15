from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFormLayout, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget


class ProfilePage(QWidget):
    def __init__(self):
        super().__init__()
        self._editing = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.back_button = QPushButton("<- Back to Dashboard")
        self.back_button.setObjectName("backButton")
        layout.addWidget(self.back_button)

        header_card = QFrame()
        header_card.setObjectName("profileHeaderCard")
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(12, 10, 12, 10)
        header_layout.setSpacing(10)

        avatar = QLabel("V")
        avatar.setObjectName("profileAvatar")
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setFixedSize(52, 52)

        title_col = QVBoxLayout()
        title_col.setContentsMargins(0, 0, 0, 0)
        title_col.setSpacing(2)

        self.profile_title = QLabel("Profile")
        self.profile_title.setObjectName("sectionTitle")
        subtitle = QLabel("Manage your account information")
        subtitle.setObjectName("stateBadge")

        title_col.addWidget(self.profile_title)
        title_col.addWidget(subtitle)

        self.edit_button = QPushButton("Edit")
        self.edit_button.setObjectName("primaryButton")
        self.edit_button.setFixedWidth(88)
        self.edit_button.clicked.connect(self._toggle_edit_mode)

        header_layout.addWidget(avatar)
        header_layout.addLayout(title_col, 1)
        header_layout.addWidget(self.edit_button, 0, Qt.AlignVCenter)

        layout.addWidget(header_card)

        form_card = QFrame()
        form_card.setObjectName("profileFormCard")
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(12, 12, 12, 12)
        form_layout.setSpacing(8)

        form = QFormLayout()
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(10)

        self.name_input = QLineEdit("Vivek")
        self.email_input = QLineEdit("bsvivek2003@gmail.com")
        self.phone_input = QLineEdit("7676815877")
        self.member_since_input = QLineEdit("Mar 8, 2026")
        self.hospital_input = QLineEdit("Indian Institute of Science")

        self._field_inputs = [
            self.name_input,
            self.email_input,
            self.phone_input,
            self.member_since_input,
            self.hospital_input,
        ]
        for field in self._field_inputs:
            field.setObjectName("profileField")

        form.addRow(self._label("Name"), self.name_input)
        form.addRow(self._label("Email"), self.email_input)
        form.addRow(self._label("Phone Number"), self.phone_input)
        form.addRow(self._label("Member Since"), self.member_since_input)
        form.addRow(self._label("Hospital/Institution"), self.hospital_input)

        form_layout.addLayout(form)
        layout.addWidget(form_card, 1)

        self._set_edit_mode(False)

    def _label(self, text):
        lbl = QLabel(text)
        lbl.setObjectName("profileKey")
        return lbl

    def _set_edit_mode(self, enabled):
        self._editing = enabled
        for field in self._field_inputs:
            field.setReadOnly(not enabled)
        self.edit_button.setText("Save" if enabled else "Edit")

    def _toggle_edit_mode(self):
        self._set_edit_mode(not self._editing)
