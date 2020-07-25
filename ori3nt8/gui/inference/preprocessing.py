import numpy as np
from PIL import Image
from PySide2.QtCore import Qt
from PySide2.QtGui import QImage
from grundzeug.container.di import Inject
from typing_extensions import Annotated

from ori3nt8.common.preprocessing import PreprocessingConfig


class PreprocessingPipeline():
    def __init__(self, preprocessing_config: Annotated[PreprocessingConfig, Inject]):
        self.resize_to = preprocessing_config.resize_to
        self.crop_to = preprocessing_config.crop_to
        self.normalization_mean = np.array(preprocessing_config.normalization_mean).reshape((3, 1, 1))
        self.normalization_std = np.array(preprocessing_config.normalization_std).reshape((3, 1, 1))

    def resize_qimage(self, image: QImage) -> QImage:
        return image.scaled(self.resize_to, self.resize_to, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

    def qimage_to_numpy(self, image: QImage) -> Image:
        image = image.convertToFormat(QImage.Format.Format_RGB32)
        width = image.width()
        height = image.height()
        ptr = image.constBits()
        arr = np.array(ptr).reshape((height, width, 4))[:, :, :3]
        return arr

    def to_chw(self, arr: np.array) -> np.array:
        arr = np.transpose(arr, (2, 0, 1))
        return arr

    def perform_crop(self, arr: np.array) -> np.array:
        _, h, w = arr.shape
        crop_top = int(round((h - self.crop_to) / 2.))
        crop_left = int(round((w - self.crop_to) / 2.))
        arr = arr[:, crop_top: crop_top + self.crop_to, crop_left: crop_left + self.crop_to]
        return arr

    def to_float(self, arr: np.array) -> np.array:
        arr = arr.astype(np.float32) / 255
        return arr

    def normalize(self, arr: np.array) -> np.array:
        arr = (arr - self.normalization_mean) / self.normalization_std
        return arr

    def preprocess(self, arr: np.array) -> np.array:
        arr = self.to_chw(arr)
        arr = self.perform_crop(arr)
        arr = self.to_float(arr)
        arr = self.normalize(arr)
        return arr.astype(np.float32)

    def image_to_input_tensor(self, image):
        image = self.resize_qimage(image)
        arr = self.qimage_to_numpy(image)
        arr = self.preprocess(arr)
        return arr
