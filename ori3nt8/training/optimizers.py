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

from grundzeug.config import configuration, Configurable
from grundzeug.container.di import InjectAnnotation
from torch import optim as optim
from torch.optim import Optimizer
from typing_extensions import Annotated


class AbstractOptimizerFactory(ABC):
    @abstractmethod
    def create(self, parameters) -> Optimizer:
        raise NotImplementedError()


@configuration(["optimizers", "adam"])
class AdamConfig():
    learning_rate: float = Configurable[float](
        ["learning_rate"],
        default=1e-4,
        description="Adam's initial learning rate"
    )
    beta1: float = Configurable[float](
        ["beta1"],
        default=0.9,
        description="Adam's beta1 parameter"
    )
    beta2: float = Configurable[float](
        ["beta2"],
        default=0.999,
        description="Adam's beta2 parameter"
    )
    weight_decay: float = Configurable[float](
        ["weight_decay"],
        default=1e-4,
        description="Weight decay"
    )


class AdamOptimizerFactory(AbstractOptimizerFactory):
    def __init__(self, adam_config: Annotated[AdamConfig, InjectAnnotation[AdamConfig]]):
        self.adam_config: AdamConfig = adam_config

    def create(self, parameters) -> Optimizer:
        return optim.Adam(
            parameters,
            lr=self.adam_config.learning_rate,
            weight_decay=self.adam_config.weight_decay,
            betas=(self.adam_config.beta1, self.adam_config.beta2)
        )
