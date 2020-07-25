from typing import Callable

import numpy as np
import scipy
import scipy.special
from PySide2.QtCore import QRunnable, Slot, QObject, Signal
from PySide2.QtGui import QImage
from grundzeug.container.di import Inject
from typing_extensions import Annotated

from ori3nt8.gui.inference.executors import AbstractExecutor
from ori3nt8.gui.inference.preprocessing import PreprocessingPipeline


class OrientationSuggestionRunnableSignals(QObject):
    result_changed = Signal(int, int, str)
    processing_started = Signal()
    processing_completed = Signal()


class OrientationSuggestionRunnable(QRunnable):
    def __init__(
            self,
            path: str,
            original_orientation: int,
            image: QImage,
            orientation_nn_executor: AbstractExecutor,
            remove_runnable_callback: Callable[[], None],
            preprocessing_pipeline: Annotated[PreprocessingPipeline, Inject]
    ):
        super().__init__()
        self.remove_runnable_callback: Callable[[], None] = remove_runnable_callback
        self.path: str = path
        self.original_rotation: int = original_orientation
        self.signals = OrientationSuggestionRunnableSignals()
        self.image: QImage = image
        self.orientation_nn_executor: AbstractExecutor = orientation_nn_executor
        self.preprocessing_pipeline = preprocessing_pipeline

    @Slot()
    def run(self):
        self.signals.processing_started.emit()
        try:
            image = self.image
            if image is None:
                self.signals.result_changed.emit(0)
                self.signals.processing_completed.emit()
                return

            arr = self.preprocessing_pipeline.image_to_input_tensor(image)
            batched_arr = self.create_batch_array(arr)
            res = self.orientation_nn_executor(batched_arr)
            res = self.postprocess(res)
            self.signals.result_changed.emit(int(res), self.original_rotation, self.path)
        finally:
            self.remove_runnable_callback()
            self.signals.processing_completed.emit()

    def create_batch_array(self, arr: np.array) -> np.array:
        arr1 = np.expand_dims(arr, axis=0)
        arr2 = np.rot90(arr1, axes=(2, 3))
        arr3 = np.rot90(arr2, axes=(2, 3))
        arr4 = np.rot90(arr3, axes=(2, 3))
        batched_arr = np.concatenate([arr1, arr2, arr3, arr4], axis=0)
        return batched_arr

    def postprocess(self, res: np.array) -> np.ndarray:
        res = scipy.special.softmax(res, axis=-1)
        for i in range(4):
            res[i, :] = np.roll(res[i, :], -i)
        res = np.mean(res, axis=0)
        res = np.argmax(res, axis=-1)
        return res
