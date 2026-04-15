import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication


def _ensure_project_root_on_path() -> None:
    # Allow `python main.py` from any working directory.
    project_root = Path(__file__).resolve().parent
    root_str = str(project_root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)


def run() -> int:
    _ensure_project_root_on_path()

    from Frontend.ui_main_window import MainWindow

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(run())
