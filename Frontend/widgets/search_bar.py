from PySide6.QtWidgets import QLineEdit


class SearchBar(QLineEdit):
    def __init__(self):
        super().__init__()
        self.setPlaceholderText("Search patients by UHID, GMA, or Name...")
        self.setObjectName("searchBar")
