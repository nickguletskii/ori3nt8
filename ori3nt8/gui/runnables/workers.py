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

from PySide2.QtCore import QThreadPool, QObject
from PySide2.QtGui import QImage
from grundzeug.container import Injector
from grundzeug.container.di import Inject
from typing_extensions import Annotated

from ori3nt8.gui.inference.executors import AbstractExecutor
from ori3nt8.gui.inference.runnable import OrientationSuggestionRunnable
from ori3nt8.gui.runnables.ImageRenderRunnable import ImageReaderRunnable
from ori3nt8.gui.runnables.MetadataReplacementRunnable import MetadataReplacementRunnable
from ori3nt8.gui.utils.concurrency import SingleRunnableManager


class ImageWorkers(QObject):
    def __init__(
            self,
            executor: Annotated[AbstractExecutor, Inject],
            injector: Annotated[Injector, Inject]
    ):
        super().__init__()

        image_loading_callback = QThreadPool(self)
        image_loading_callback.setMaxThreadCount(1)
        self._image_reading_manager = SingleRunnableManager(image_loading_callback)

        secondary_threadpool = QThreadPool(self)
        self._image_writing_manager = SingleRunnableManager(secondary_threadpool)
        self._orientation_suggestion_manager = SingleRunnableManager(secondary_threadpool)
        self.orientation_suggestion_runnable_factory = injector.inject(OrientationSuggestionRunnable)

        self.orientation_nn_executor = executor

    def schedule_image_reading(
            self,
            path: Path,
            processing_completed_callback: Callable[[QImage, str], None]
    ):
        runnable = ImageReaderRunnable(
            path=path,
            remove_runnable_callback=self._image_reading_manager.remove_runnable
        )
        runnable.signals.processing_completed.connect(processing_completed_callback)
        self._image_reading_manager.start(runnable)

    def schedule_metadata_replacement(
            self,
            path: Path,
            orientation: int,
            flip: int
    ):
        runnable = MetadataReplacementRunnable(
            path=path,
            orientation=orientation,
            flip=flip,
            remove_runnable_callback=self._image_writing_manager.remove_runnable
        )
        self._image_writing_manager.start(runnable)

    def schedule_suggestion_prediction(
            self,
            path: Path,
            orientation: int,
            image: QImage,
            result_changed_callback: Callable[[int, int, str], None],
            processing_started_callback: Callable[[], None],
            processing_completed_callback: Callable[[], None]
    ):
        runnable = self.orientation_suggestion_runnable_factory(
            path=str(path),
            original_orientation=orientation,
            image=image,
            orientation_nn_executor=self.orientation_nn_executor,
            remove_runnable_callback=self._orientation_suggestion_manager.remove_runnable
        )
        runnable.signals.result_changed.connect(result_changed_callback)
        runnable.signals.processing_started.connect(processing_started_callback)
        runnable.signals.processing_completed.connect(processing_completed_callback)
        self._orientation_suggestion_manager.start(runnable)
