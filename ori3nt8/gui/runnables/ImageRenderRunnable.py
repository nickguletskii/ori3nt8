from pathlib import Path
from typing import Callable

from PySide2.QtCore import QRunnable, Slot, QObject, Signal
from PySide2.QtGui import QImageReader, QImage


class ImageReaderRunnable(QRunnable):
    def __init__(self, path: Path, remove_runnable_callback: Callable[[], None]):
        super().__init__()
        self.remove_runnable_callback = remove_runnable_callback
        self.path = path
        self.signals = ImageReaderRunnableSignals()

    @Slot()
    def run(self):
        image = QImageReader(str(self.path)).read()
        self.remove_runnable_callback()
        self.signals.processing_completed.emit(image, str(self.path))


class ImageReaderRunnableSignals(QObject):
    processing_completed = Signal(QImage, str)
