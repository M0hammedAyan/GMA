from PySide6.QtWidgets import QApplication

from Frontend.ui_main_window import MainWindow


def run():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    run()
