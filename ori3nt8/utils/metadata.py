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

from io import BytesIO
from pathlib import Path
from typing import Tuple

import piexif
from PySide2.QtCore import QSaveFile, QFile, QByteArray, QIODevice

ROT_TO_EXIF = {
    (0, 0): 1, (3, 0): 8, (2, 0): 3, (1, 0): 6,
    (0, 1): 2, (3, 1): 7, (2, 1): 4, (1, 1): 5,
}
EXIF_TO_ROT = {v: k for k, v in ROT_TO_EXIF.items()}


def load_exif_data(path: Path) -> Tuple[int, bool]:
    """
    Loads the EXIF metadata from the specified image.

    Parameters
    ----------
    path
        The path to the image whose orientation and flip value should be retrieved.

    Returns
    -------
    The first value in the tuple contains the number of clockwise rotations that have to be applied to correctly orient
    the image. The second value contains 0 if the image is not flipped, and 1 if the image is flipped horizontally.

    """
    file = QFile(str(path))
    file.open(QIODevice.ReadOnly)
    if not file.isOpen():
        raise Exception(f"Couldn't open {path} for writing!")
    data = file.readAll()
    exif_dict = piexif.load(data.data())
    if "0th" in exif_dict and piexif.ImageIFD.Orientation in exif_dict["0th"]:
        orient = exif_dict["0th"][piexif.ImageIFD.Orientation]
        if orient not in EXIF_TO_ROT:
            # Fall back to default (correct) orientation
            orient = 1
        orientation, flip = EXIF_TO_ROT[orient]
    else:
        orientation, flip = 0, 0
    return orientation, flip


def replace_exif_orientation(path: Path, orientation: int, flip: int) -> None:
    """
    Replaces the EXIF orientation metadata in the image pointed to by the `path`.

    Parameters
    ----------
    path
        The path to the image whose orientation should be changed.
    orientation
        The number of clockwise rotations that have to be applied to correctly orient the image.
    flip
        EXIF orientation supports horizontally flipped images. Ori3nt8 simply preserves the flip value from the original
        metadata.
    """
    data_str = _read_jpeg_bytes(path)
    exif_dict = piexif.load(data_str)
    orient = ROT_TO_EXIF[(orientation, flip)]
    exif_dict["0th"][piexif.ImageIFD.Orientation] = orient
    exif_bytes = piexif.dump(exif_dict)
    new_file_bytes_io = BytesIO()
    piexif.insert(exif_bytes, data_str, new_file=new_file_bytes_io)
    _write_jpeg_bytes(new_file_bytes_io, path)


def _read_jpeg_bytes(path):
    file = QFile(str(path))
    file.open(QIODevice.ReadOnly)
    if not file.isOpen():
        raise Exception(f"Couldn't open {path} for reading!")
    data = file.readAll()
    data_str = data.data()
    return data_str


def _write_jpeg_bytes(new_file_bytes_io, path):
    file = QSaveFile(str(path))
    file.open(QIODevice.WriteOnly)
    if not file.isOpen():
        raise Exception(f"Couldn't open {path} for writing!")
    try:
        file.seek(0)
        file.resize(0)
        new_file_bytes_io.seek(0)
        file.write(QByteArray(new_file_bytes_io.read()))
        file.commit()
    except:
        file.cancelWriting()
        raise
