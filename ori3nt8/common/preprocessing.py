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