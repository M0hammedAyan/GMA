from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout


class UserInfoCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("panel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        title = QLabel("User Info")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(5)

        rows = [
            ("Full Name", "Vivek"),
            ("Email", "bsvivek2003@gmail.com"),
            ("Phone", "7676815877"),
            ("Member Since", "Mar 8, 2026"),
            ("Hospital", "Indian Institute of Science"),
        ]

        for idx, (key, value) in enumerate(rows):
            key_lbl = QLabel(key)
            key_lbl.setObjectName("profileKey")
            val_lbl = QLabel(value)
            val_lbl.setObjectName("profileValue")
            grid.addWidget(key_lbl, idx, 0)
            grid.addWidget(val_lbl, idx, 1)

        layout.addLayout(grid)
