from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget


class HeaderWidget(QFrame):
    tabChanged = Signal(int)
    themeToggled = Signal(bool)

    def __init__(self):
        super().__init__()
        self.setObjectName("topHeader")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(12)

        self.title_label = QLabel("GMA")
        self.title_label.setObjectName("appTitle")

        top_row.addWidget(self.title_label)
        top_row.addStretch(1)

        self.dark_toggle = QPushButton()
        self.dark_toggle.setCheckable(True)
        self.dark_toggle.setChecked(False)
        self.dark_toggle.setObjectName("themeToggle")
        self.dark_toggle.clicked.connect(self._on_theme_clicked)
        self._update_theme_toggle_label()

        self.user_button = QPushButton("👤 Vivek")
        self.user_button.setObjectName("userButton")

        top_row.addWidget(self.dark_toggle)
        top_row.addWidget(self.user_button)
        layout.addLayout(top_row)

        divider = QFrame()
        divider.setObjectName("headerDivider")
        divider.setFixedHeight(1)
        layout.addWidget(divider)

        self.nav_container = QWidget()
        nav_row = QHBoxLayout(self.nav_container)
        nav_row.setContentsMargins(0, 0, 0, 0)
        nav_row.setSpacing(10)

        self.tabs = []
        tab_variants = ["dashboard", "patients", "uploads"]
        for idx, label in enumerate(["Dashboard", "Patients", "Uploads"]):
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setObjectName("navTab")
            btn.setProperty("tabVariant", tab_variants[idx])
            btn.clicked.connect(lambda _checked=False, i=idx: self._on_tab_clicked(i))
            self.tabs.append(btn)
            nav_row.addWidget(btn)
        nav_row.addStretch(1)
        layout.addWidget(self.nav_container)

        self.set_active_tab(0)

    def _on_tab_clicked(self, index):
        self.set_active_tab(index)
        self.tabChanged.emit(index)

    def _on_theme_clicked(self):
        self._update_theme_toggle_label()
        self.themeToggled.emit(self.dark_toggle.isChecked())

    def _update_theme_toggle_label(self):
        # Checked = dark mode (moon), unchecked = light mode (sun)
        self.dark_toggle.setText("☾" if self.dark_toggle.isChecked() else "☀")

    def set_active_tab(self, index):
        for i, btn in enumerate(self.tabs):
            btn.setChecked(i == index)

    def set_tabs_visible(self, visible):
        self.nav_container.setVisible(visible)
