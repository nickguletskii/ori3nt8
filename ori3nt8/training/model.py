from typing_extensions import Annotated

import torch
from grundzeug.config import inject_config
from grundzeug.container.di import InjectAnnotation
from pytorch_lightning import LightningModule
from torch.nn import functional as F
from torch.optim import lr_scheduler as lr_scheduler
from torch.utils.data import ConcatDataset
from torchvision import transforms as transforms

from ori3nt8.training.common import TrainingConfig, DatasetConfig
from ori3nt8.training.data import ImageFolderDataset, RotateNTimesTransform
from ori3nt8.training.metrics import calculate_accuracy
from ori3nt8.training.models import AbstractModelFactory
from ori3nt8.training.optimizers import AbstractOptimizerFactory
from ori3nt8.training.preprocessing import AbstractPreprocessingFactory


class Ori3nt8LightningModel(LightningModule):
    def __init__(
            self,
            pretrained: bool,
            model_factory: Annotated[AbstractModelFactory, InjectAnnotation[AbstractModelFactory]],
            optimizer_factory: Annotated[AbstractOptimizerFactory, InjectAnnotation[AbstractOptimizerFactory]],
            preprocessing_factory: Annotated[AbstractPreprocessingFactory, InjectAnnotation[AbstractPreprocessingFactory]],
            dataset_config: Annotated[DatasetConfig, InjectAnnotation[DatasetConfig]],
            batch_size: int = inject_config(TrainingConfig.batch_size),
            epochs: int = inject_config(TrainingConfig.epochs),
            **kwargs
    ):
        super().__init__()
        self.epochs = epochs
        self.batch_size = batch_size
        self.preprocessing_factory: AbstractPreprocessingFactory = preprocessing_factory
        self.optimizer_factory: AbstractOptimizerFactory = optimizer_factory
        self.dataset_config: DatasetConfig = dataset_config
        self.pretrained = pretrained
        self.model = model_factory.create()

    def forward(self, x):
        return self.model(x)

    def training_step(self, batch, batch_idx):
        images, target = batch
        output = self(images)
        loss_val = F.cross_entropy(output, target)
        acc = calculate_accuracy(output, target)

        tqdm_dict = {"train_loss": loss_val}
        return {
            "loss": loss_val,
            "acc": acc,
            "progress_bar": tqdm_dict,
            "log": tqdm_dict
        }

    def validation_step(self, batch, batch_idx):
        images, target = batch
        output = self(images)
        loss_val = F.cross_entropy(output, target)
        acc = calculate_accuracy(output, target)

        return {
            "val_loss": loss_val,
            "val_acc": acc
        }

    def validation_epoch_end(self, outputs):
        tqdm_dict = {}
        for metric_name in ["val_loss", "val_acc"]:
            metric_total = 0
            for output in outputs:
                metric_value = output[metric_name]
                metric_total += float(metric_value)
            tqdm_dict[metric_name] = metric_total / len(outputs)

        result = {"progress_bar": tqdm_dict, "log": tqdm_dict, "val_loss": tqdm_dict["val_loss"]}
        return result

    def configure_optimizers(self):
        optimizer = self.optimizer_factory.create(self.parameters())
        scheduler = lr_scheduler.CosineAnnealingLR(optimizer, self.epochs, eta_min=1e-7)
        return [optimizer], [scheduler]

    def train_dataloader(self):
        train_dataset = ImageFolderDataset(
            self.dataset_config.training_path,
            self.preprocessing_factory.create_training_transform()
        )

        train_loader = torch.utils.data.DataLoader(
            dataset=train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=self.batch_size
        )
        return train_loader

    def val_dataloader(self):
        val_loader = torch.utils.data.DataLoader(
            ConcatDataset(
                [
                    ImageFolderDataset(
                        self.dataset_config.validation_path,
                        transforms.Compose([
                            self.preprocessing_factory.create_validation_transform(),
                            RotateNTimesTransform(n_rotations)
                        ])
                    )
                    for n_rotations
                    in range(4)
                ]
            ),
            batch_size=self.batch_size // 2,
            shuffle=False,
            num_workers=self.batch_size
        )
        return val_loader
