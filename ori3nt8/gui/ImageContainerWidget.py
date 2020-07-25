from pathlib import Path
from typing import Callable, Optional

import PySide2
from PySide2.QtCore import QRect, QPointF
from PySide2.QtGui import QImage, QPainter, Qt, QPen, QPalette
from PySide2.QtWidgets import QWidget
from grundzeug.container.di import Inject
from typing_extensions import Annotated

from ori3nt8.gui.metadata.common import Metadata, AbstractMetadataStorage
from ori3nt8.gui.metadata.sql import SqliteMetadataStorage
from ori3nt8.gui.utils.rendering import draw_text
from ori3nt8.gui.runnables.workers import ImageWorkers
from ori3nt8.utils.metadata import load_exif_data

ORIENTATION_TO_STR = {
    0: "No rotation",
    1: "Rotated clockwise",
    2: "Rotated 180 degrees",
    3: "Rotated counter-clockwise"
}


class ImageContainerWidget(QWidget):
    def __init__(
            self,
            status_bar_callback: Callable[[str], None],
            image_workers: Annotated[ImageWorkers, Inject],
            metadata_storage_engine: Annotated[AbstractMetadataStorage, Inject]
    ):
        super().__init__()
        self.status_bar_callback = status_bar_callback
        self.image: Optional[QImage] = None
        self.path: Optional[Path] = None
        self.orientation: int = 0
        self.suggested_orientation: Optional[int] = None
        self.flip: int = 0
        self.original_orientation: int = 0
        self.orientation_was_selected_manually: bool = False
        self.orientation_was_selected_automatically: bool = False
        self.apply_automaticaly: bool = True
        self.loading: bool = False
        self.apply_next_orientation_suggestion: bool = False

        self.orientation_prediction_working_count = 0
        self._image_workers = image_workers

        self.metadata_storage_engine: AbstractMetadataStorage = metadata_storage_engine

        self.update_progressbar()

    def set_image_path(self, path: Path):
        path = path.absolute()
        self.apply_next_orientation_suggestion = False
        if not path.is_file():
            self.clear_image()
            return
        self.loading = True
        self.repaint()

        self._image_workers.schedule_image_reading(path, self._finish_loading_image)

    def _finish_loading_image(self, image: QImage, path: str):
        path = Path(path)
        self.loading = False
        if image.width() == 0:
            self.clear_image()
            return
        self.image = image
        self.path = path
        orientation, flip = load_exif_data(path)
        metadata = self.metadata_storage_engine.load(Path(path))
        if metadata is None:
            metadata = Metadata(
                original_orientation=orientation
            )
        self.flip = flip
        self.original_orientation = metadata.original_orientation
        self.suggested_orientation = None
        self.orientation_was_selected_manually = metadata.orientation_was_selected_manually
        self.orientation_was_selected_automatically = metadata.orientation_was_selected_automatically
        self.set_orientation(orientation)
        self.repaint()
        self._image_workers.schedule_suggestion_prediction(
            path=path,
            orientation=orientation,
            image=image,
            result_changed_callback=self.update_suggested_orientation,
            processing_started_callback=self.orientation_prediction_processing_started,
            processing_completed_callback=self.orientation_prediction_processing_completed,
        )
        self.update_progressbar()

    def clear_image(self):
        self.image = None
        self.path = None
        self.flip = 0
        self.original_orientation = 0
        self.suggested_orientation = None
        self.orientation_was_selected_manually = False
        self.orientation_was_selected_automatically = False
        self.set_orientation(0)
        self.update_progressbar()
        self.repaint()

    def set_apply_automatically(self, apply_automatically):
        self.apply_automaticaly = apply_automatically

    def update_suggested_orientation(
            self,
            suggested_orientation: int,
            original_orientation: int,
            path: str
    ):
        if str(self.path) != path:
            # Outdated analysis: the user has switched to a different image, discard
            return

        self.suggested_orientation = suggested_orientation

        if (self.apply_automaticaly
            and self.orientation == self.original_orientation
            and not self.orientation_was_selected_manually) \
                or self.apply_next_orientation_suggestion:
            self.apply_next_orientation_suggestion = False
            self.set_orientation(suggested_orientation)
        self.update_progressbar()
        self.repaint()

        self.dump_metadata()

    def apply_suggested_orientation(self):
        if self.suggested_orientation is None:
            self.apply_next_orientation_suggestion = True
            return

        self.orientation_was_selected_manually = False
        self.orientation_was_selected_automatically = True
        self.set_orientation(self.suggested_orientation)
        self.repaint()

        self.dump_metadata()

    def dump_metadata(self):
        self.metadata_storage_engine.dump(
            self.path,
            Metadata(
                original_orientation=self.original_orientation,
                suggested_orientation=self.suggested_orientation,
                orientation_was_selected_manually=self.orientation_was_selected_manually,
                orientation_was_selected_automatically=self.orientation_was_selected_automatically,
            )
        )

    def set_orientation(self, orientation):
        self.orientation = orientation

        if self.image is not None:
            if self.orientation is not None:
                self._image_workers.schedule_metadata_replacement(
                    path=self.path,
                    orientation=self.orientation,
                    flip=self.flip
                )
        self.update_progressbar()

    def orientation_prediction_processing_started(self):
        self.orientation_prediction_working_count += 1
        self.update_progressbar()

    def orientation_prediction_processing_completed(self):
        self.orientation_prediction_working_count -= 1
        self.update_progressbar()

    def update_progressbar(self):
        if self.path is None:
            message = f"Open a directory and select an image to continue."
            self.status_bar_callback(message)
            return
        message = f"Original orientation: {ORIENTATION_TO_STR[self.original_orientation]}, "

        if self.orientation_prediction_working_count > 0 or self.suggested_orientation is None:
            message += "working on suggestion..."
        else:
            message += f"suggested orientation: {ORIENTATION_TO_STR[self.suggested_orientation]}"
        self.status_bar_callback(message)

    def rotate_clockwise(self):
        self.orientation_was_selected_manually = True
        self.orientation_was_selected_automatically = False
        self.set_orientation((self.orientation + 1) % 4)
        self.repaint()
        self.update_progressbar()

        self.dump_metadata()

    def rotate_counterclockwise(self):
        self.orientation_was_selected_manually = True
        self.orientation_was_selected_automatically = False
        self.set_orientation((self.orientation - 1) % 4)
        self.repaint()
        self.update_progressbar()

        self.dump_metadata()

    def paintEvent(self, event: PySide2.QtGui.QPaintEvent):
        painter = QPainter(self)

        if self.orientation is None:
            return
        if self.image is not None:
            painter.save()
            image_width = self.image.width()
            image_height = self.image.height()
            if self.orientation % 2 == 0:
                scale = min(self.width() / image_width, self.height() / image_height)
            else:
                scale = min(self.width() / image_height, self.height() / image_width)

            target_width = image_width * scale
            target_height = image_height * scale
            padding_left = (self.width() - target_width) // 2
            padding_top = (self.height() - target_height) // 2
            painter.translate(self.width() / 2, self.height() / 2)
            painter.rotate(90 * self.orientation)
            painter.translate(-self.width() / 2, -self.height() / 2)
            painter.drawImage(QRect(padding_left, padding_top, target_width, target_height), self.image)
            painter.restore()

            if self.original_orientation is not None:
                painter.save()
                self.render_orientation_indicator(
                    painter,
                    self.original_orientation,
                    target_height,
                    target_width,
                    pen_color=Qt.yellow,
                    brush_color=Qt.darkYellow
                )
                painter.restore()
            if self.suggested_orientation is not None:
                painter.save()
                self.render_orientation_indicator(
                    painter,
                    self.suggested_orientation,
                    target_height,
                    target_width,
                    pen_color=Qt.green,
                    brush_color=Qt.darkGreen
                )
                painter.restore()
        if self.loading:
            painter.save()
            painter.setPen(self.palette().brush(QPalette.Foreground).color())
            font = painter.font()
            font.setPointSize(font.pointSize() * 2)
            painter.setFont(font)
            draw_text(painter, self.width() / 2, self.height() / 2, Qt.AlignVCenter | Qt.AlignHCenter, "Loading...")
            painter.restore()

    def render_orientation_indicator(
            self,
            painter,
            suggested_orientation,
            target_height,
            target_width,
            pen_color,
            brush_color
    ):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)
        relative_orientation = (suggested_orientation - self.orientation) % 4
        triangle_size = 16
        if relative_orientation % 2 == 1:
            if self.orientation % 2 == 0:
                sz = target_width
            else:
                sz = target_height
            ch = self.height() / 2
            p1 = QPointF(0, ch - triangle_size)
            p2 = QPointF(0, ch + triangle_size)
            p3 = QPointF(triangle_size, ch)

            def update_x(ct, p, sz):
                px = (self.width() - sz) / 2
                p.setX(p.x() + px if ct // 2 == 0 else self.width() - px - p.x())

            update_x(relative_orientation, p1, sz)
            update_x(relative_orientation, p2, sz)
            update_x(relative_orientation, p3, sz)
        else:
            if self.orientation % 2 == 0:
                sz = target_height
            else:
                sz = target_width
            cw = self.width() / 2
            p1 = QPointF(cw - triangle_size, 0)
            p2 = QPointF(cw + triangle_size, 0)
            p3 = QPointF(cw, triangle_size)

            def update_y(ct, p, sz):
                py = (self.height() - sz) / 2
                p.setY(p.y() + py if ct // 2 == 0 else self.height() - p.y() - py)

            update_y(relative_orientation, p1, sz)
            update_y(relative_orientation, p2, sz)
            update_y(relative_orientation, p3, sz)
        painter.setPen(QPen(pen_color, 1))
        painter.setBrush(brush_color)
        painter.drawPolygon([p1, p2, p3])
