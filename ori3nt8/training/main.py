import random
from pathlib import Path

import torch
import torch.nn.parallel
import torch.utils.data
import torch.utils.data.distributed
from grundzeug.config import configuration, Configurable
from pytorch_lightning import Trainer
from pytorch_lightning.callbacks import ModelCheckpoint

from ori3nt8.training.common import DatasetConfig, TrainingConfig
from ori3nt8.training.containers import build_container
from ori3nt8.training.model import Ori3nt8LightningModel
from ori3nt8.training.models import AbstractModelFactory, EfficientNetModelFactory, EfficientNetConfig
from ori3nt8.training.optimizers import AbstractOptimizerFactory, AdamOptimizerFactory, AdamConfig
from ori3nt8.training.preprocessing import AbstractPreprocessingFactory, DefaultPreprocessingFactory
from ori3nt8.common.preprocessing import PreprocessingConfig


@configuration(["trainer"])
class TrainerConfig():
    checkpoint_path: Path = Configurable[Path](
        ["checkpoint_path"],
        default=Path("checkpoints"),
        description="The output path for the checkpoints"
    )
    default_root_dir: Path = Configurable[Path](
        ["default_root_dir"],
        default=Path("."),
        description="The output path for PyTorch Lightning logs"
    )
    gpus: int = Configurable[int](
        ["gpus"],
        default=1,
        description="Number of GPUs to use for training"
    )
    precision: int = Configurable[int](
        ["precision"],
        default=16,
        description="Training precision, set to 16 for half-precision training using APEX or 32 for full-precision"
                    "training."
    )
    seed: int = Configurable[int](
        ["seed"],
        default=42,
        description="The random seed to set before training"
    )


def main() -> None:
    container = build_container(
        [TrainerConfig, DatasetConfig, TrainingConfig, EfficientNetConfig, AdamConfig, PreprocessingConfig]
    )
    container.register_type[AbstractOptimizerFactory, AdamOptimizerFactory]()
    container.register_type[AbstractModelFactory, EfficientNetModelFactory]()
    container.register_type[AbstractPreprocessingFactory, DefaultPreprocessingFactory]()

    trainer_config: TrainerConfig = container.resolve[TrainerConfig]()
    epochs: int = container.resolve[TrainingConfig.epochs]()

    model = container.inject(Ori3nt8LightningModel)(pretrained=True)

    random.seed(trainer_config.seed)
    torch.manual_seed(trainer_config.seed)

    checkpoint_callback = ModelCheckpoint(
        filepath=str(trainer_config.checkpoint_path / "weights.ckpt"),
        save_top_k=1,
        verbose=True,
        monitor="val_acc",
        mode="max"
    )

    trainer = Trainer(
        default_root_dir=str(trainer_config.default_root_dir),
        gpus=trainer_config.gpus,
        max_epochs=epochs,
        precision=trainer_config.precision,
        checkpoint_callback=checkpoint_callback,
        benchmark=True,
        deterministic=True
    )

    trainer.fit(model)


if __name__ == "__main__":
    main()
