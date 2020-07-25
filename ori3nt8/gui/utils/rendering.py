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

from PySide2.QtCore import QPointF, QRectF
from PySide2.QtGui import QPainter, Qt


def draw_text(painter: QPainter, x: float, y: float, flags, text: str):
    # Originally from
    # https://stackoverflow.com/questions/24831484/how-to-align-qpainter-drawtext-around-a-point-not-a-rectangle
    size = 32767.0
    corner = QPointF(x, y - size)
    if flags & Qt.AlignHCenter:
        corner.setX(corner.x() - size / 2.0)
    elif flags & Qt.AlignRight:
        corner.setX(corner.x() - size)
    if flags & Qt.AlignVCenter:
        corner.setY(corner.y() + size / 2.0)
    elif flags & Qt.AlignTop:
        corner.setY(corner.y() + size)
    else:
        flags |= Qt.AlignBottom
    rect = QRectF(corner.x(), corner.y(), size, size)
    painter.drawText(rect, int(flags), text)
