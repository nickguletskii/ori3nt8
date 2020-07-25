import sys
from pathlib import Path


def running_in_pyinstaller():
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def root_path():
    if running_in_pyinstaller():
        return Path(sys._MEIPASS).absolute()
    return Path(__file__).parent.parent.parent.absolute()


def resource_path() -> Path:
    return root_path() / "resources"
