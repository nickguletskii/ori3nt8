from pathlib import Path
from typing import Callable

from PySide2.QtCore import QRunnable, Slot

from ori3nt8.utils.metadata import replace_exif_orientation


class MetadataReplacementRunnable(QRunnable):
    def __init__(
            self,
            path: Path,
            orientation: int,
            flip: int,
            remove_runnable_callback: Callable[[], None]
    ):
        super().__init__()
        self.remove_runnable_callback = remove_runnable_callback
        self.path = path
        self.orientation = orientation
        self.flip = flip

    @Slot()
    def run(self):
        replace_exif_orientation(
            self.path,
            orientation=self.orientation,
            flip=self.flip
        )
        self.remove_runnable_callback()
