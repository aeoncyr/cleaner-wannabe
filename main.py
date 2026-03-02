import sys
import os
import importlib.util
from pathlib import Path

def _prepare_pyside6_dlls():
    spec = importlib.util.find_spec("PySide6")
    if not spec or not spec.origin:
        return

    pyside_dir = Path(spec.origin).parent
    if hasattr(os, "add_dll_directory"):
        os.add_dll_directory(str(pyside_dir))
        plugins_dir = pyside_dir / "plugins"
        if plugins_dir.exists():
            os.add_dll_directory(str(plugins_dir))

    # Avoid Qt DLL conflicts from Anaconda in PATH for this process
    path = os.environ.get("PATH", "")
    if path:
        filtered = []
        for entry in path.split(";"):
            if entry and "anaconda3\\library\\bin" in entry.lower():
                continue
            filtered.append(entry)
        os.environ["PATH"] = ";".join(filtered)


_prepare_pyside6_dlls()

from PySide6.QtWidgets import QApplication  # noqa: E402
from gui_qt.app import CleanerApp  # noqa: E402

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CleanerApp()
    window.show()
    sys.exit(app.exec())
