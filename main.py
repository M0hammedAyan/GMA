import sys
import traceback
import faulthandler
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
    faulthandler.enable(all_threads=True)

    from Frontend.ui_main_window import MainWindow

    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        return app.exec()
    except Exception as err:
        print(f"Fatal application error: {err}", file=sys.stderr)
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(run())
