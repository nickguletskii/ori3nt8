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
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Metadata:
    original_orientation: int
    suggested_orientation: Optional[int] = None
    orientation_was_selected_manually: bool = False
    orientation_was_selected_automatically: bool = False


class AbstractMetadataStorage(ABC):
    @abstractmethod
    def dump(self, path: Path, metadata: Metadata):
        raise NotImplementedError()

    @abstractmethod
    def load(self, path: Path) -> Metadata:
        raise NotImplementedError()
