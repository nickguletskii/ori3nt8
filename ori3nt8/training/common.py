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