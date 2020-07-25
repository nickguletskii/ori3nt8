#  Copyright 2020 Nick Guletskii
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

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
