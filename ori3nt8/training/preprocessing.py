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

from grundzeug.container.di import InjectAnnotation
from torchvision import transforms as transforms
from typing_extensions import Annotated

from ori3nt8.common.preprocessing import PreprocessingConfig
from ori3nt8.training.data import ApplyTransformToImage, RandomRotateTransform


class AbstractPreprocessingFactory(ABC):
    @abstractmethod
    def create_training_transform(self):
        raise NotImplementedError()

    @abstractmethod
    def create_validation_transform(self):
        raise NotImplementedError()


class DefaultPreprocessingFactory(AbstractPreprocessingFactory):
    def __init__(
            self,
            preprocessing_config: Annotated[PreprocessingConfig, InjectAnnotation[PreprocessingConfig]]
    ):
        self.preprocessing_config = preprocessing_config

    def create_training_transform(self):
        return transforms.Compose([
            ApplyTransformToImage(
                transforms.Compose([
                    transforms.Resize(self.preprocessing_config.resize_to),
                    transforms.ColorJitter(brightness=0.4, saturation=0.4, contrast=0.4, hue=0.4),
                    transforms.RandomCrop(self.preprocessing_config.crop_to),
                    transforms.ToTensor(),
                    transforms.Normalize(
                        mean=self.preprocessing_config.normalization_mean,
                        std=self.preprocessing_config.normalization_std,
                    ),
                ])),
            RandomRotateTransform()
        ])

    def create_validation_transform(self):
        return ApplyTransformToImage(
            transforms.Compose([
                transforms.Resize(self.preprocessing_config.resize_to),
                transforms.CenterCrop(self.preprocessing_config.crop_to),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=self.preprocessing_config.normalization_mean,
                    std=self.preprocessing_config.normalization_std,
                ),
            ])
        )
