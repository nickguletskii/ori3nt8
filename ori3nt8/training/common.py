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

from grundzeug.config import configuration, Configurable


@configuration(["training"])
class TrainingConfig():
    batch_size: int = Configurable[int](
        ["batch_size"],
        default=32,
        description="Batch size"
    )
    epochs: int = Configurable[int](
        ["epochs"],
        default=30,
        description="Number of epochs to train for"
    )


@configuration(["datasets"])
class DatasetConfig():
    training_path: Path = Configurable[Path](
        ["training", "path"],
        description="Path to the directory containing the training dataset",
    )
    validation_path: Path = Configurable[Path](
        ["validation", "path"],
        description="Path to the directory containing the validation dataset",
    )