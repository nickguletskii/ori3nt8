from abc import ABC, abstractmethod

import numpy as np
import onnx
from caffe2.python.onnx import backend as backend

from ori3nt8.utils.resources import resource_path


class AbstractExecutor(ABC):
    @abstractmethod
    def __call__(self, images: np.ndarray) -> np.ndarray:
        raise NotImplementedError()


class Caffe2Executor():
    def __init__(self):
        onnx_model = onnx.load(str(resource_path() / "network.onnx"))
        self.rep = backend.prepare(onnx_model, device="CPU")

    def __call__(self, images: np.ndarray) -> np.ndarray:
        results = self.rep.run(images)
        return np.squeeze(results, axis=0)
