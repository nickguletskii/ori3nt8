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
