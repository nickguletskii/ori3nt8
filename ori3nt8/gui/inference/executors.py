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
