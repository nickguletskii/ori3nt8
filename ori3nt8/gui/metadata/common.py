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
