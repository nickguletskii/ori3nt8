from abc import ABC, abstractmethod
from typing import Tuple

from grundzeug.config import configuration, Configurable
from grundzeug.container.di import InjectAnnotation
from torchvision import transforms as transforms
from typing_extensions import Annotated

from ori3nt8.training.data import ApplyTransformToImage, RandomRotateTransform


class AbstractPreprocessingFactory(ABC):
    @abstractmethod
    def create_training_transform(self):
        raise NotImplementedError()

    @abstractmethod
    def create_validation_transform(self):
        raise NotImplementedError()


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
