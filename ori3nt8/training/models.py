from abc import ABC, abstractmethod

import geffnet
from grundzeug.config import configuration, Configurable
from grundzeug.container.di import InjectAnnotation
from torch.nn import Module
from typing_extensions import Annotated


class AbstractModelFactory(ABC):
    @abstractmethod
    def create(self) -> Module:
        raise NotImplementedError()


@configuration(["model", "efficientnet"])
class EfficientNetConfig():
    model_name: str = Configurable[str](
        ["model_name"],
        default="efficientnet_b1",
        description="Default name of the model that will be used as the backbone"
    )
    drop_rate: float = Configurable[float](
        ["drop_rate"],
        default=0.2,
        description="EfficientNet's drop rate"
    )
    drop_connect_rate: float = Configurable[float](
        ["drop_connect_rate"],
        default=0.2,
        description="EfficientNet's drop connect rate"
    )
    pretrained: bool = Configurable[bool](
        ["pretrained"],
        default=True,
        description="Set to true to use pretrained weights"
    )


class EfficientNetModelFactory(AbstractModelFactory):
    def __init__(self, model_config: Annotated[EfficientNetConfig, InjectAnnotation[EfficientNetConfig]]):
        self.model_config: EfficientNetConfig = model_config

    def create(self) -> Module:
        return geffnet.create_model(
            self.model_config.model_name,
            drop_rate=self.model_config.drop_rate,
            drop_connect_rate=self.model_config.drop_connect_rate,
            pretrained=self.model_config.pretrained,
            num_classes=4
        )
