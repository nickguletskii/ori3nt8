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

from typing import Tuple

from grundzeug.config import configuration, Configurable


@configuration(["preprocessing"])
class PreprocessingConfig():
    resize_to: int = Configurable[int](
        ["resize_to"],
        default=256,
        description="Default size of the image to resize to before cropping"
    )
    crop_to: int = Configurable[int](
        ["crop_to"],
        default=240,
        description="Size of the input tensor that will be passed into the CNN"
    )
    normalization_mean: Tuple[float, float, float] = Configurable[Tuple[float, float, float]](
        ["normalization_mean"],
        default=(0.485, 0.456, 0.406),
        description="The image tensor normalization mean"
    )
    normalization_std: Tuple[float, float, float] = Configurable[Tuple[float, float, float]](
        ["normalization_std"],
        default=(0.229, 0.224, 0.225),
        description="The image tensor normalization standard deviation"
    )