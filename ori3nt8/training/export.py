from io import BytesIO
from pathlib import Path

import geffnet
import onnx
import torch
from grundzeug.config import configuration, Configurable
from grundzeug.config.providers.common import ConfigurationProvider, DictTreeConfigurationProvider
from grundzeug.container.plugins import BeanList
from onnx import optimizer

from ori3nt8.training.common import DatasetConfig, TrainingConfig
from ori3nt8.training.containers import build_container
from ori3nt8.training.model import Ori3nt8LightningModel
from ori3nt8.training.models import EfficientNetConfig, EfficientNetModelFactory, AbstractModelFactory
from ori3nt8.training.optimizers import AdamConfig, AdamOptimizerFactory, AbstractOptimizerFactory
from ori3nt8.training.preprocessing import PreprocessingConfig, DefaultPreprocessingFactory, \
    AbstractPreprocessingFactory


@configuration(["export"])
class ExportConfig:
    output_path: Path = Configurable[Path](
        ["output_path"],
        default=Path("resources") / "network.onnx",
        description="The path to the output onnx file"
    )

    checkpoint_path: Path = Configurable[Path](
        ["checkpoint_path"],
        description="The path to the input checkpoint"
    )


def main() -> None:
    container = build_container(
        [DatasetConfig, ExportConfig, DatasetConfig, TrainingConfig, EfficientNetConfig, AdamConfig,
         PreprocessingConfig]
    )
    container.register_type[AbstractOptimizerFactory, AdamOptimizerFactory]()
    container.register_type[AbstractModelFactory, EfficientNetModelFactory]()
    container.register_type[AbstractPreprocessingFactory, DefaultPreprocessingFactory]()
    container.register_instance[BeanList[ConfigurationProvider]](
        DictTreeConfigurationProvider({
            "datasets": {
                "training": {
                    "path": Path("/tmp/non_existant")
                },
                "validation": {
                    "path": Path("/tmp/non_existant")
                }
            }
        })
    )

    geffnet.config.set_exportable(True)

    crop_to = container.resolve[PreprocessingConfig.crop_to]()
    export_config: ExportConfig = container.resolve[ExportConfig]()

    kwargs = container.get_kwargs_to_inject(Ori3nt8LightningModel)

    model = Ori3nt8LightningModel.load_from_checkpoint(
        checkpoint_path=str(export_config.checkpoint_path),
        **kwargs
    )

    model.freeze()

    x = torch.normal(0, 1, size=(4, 3, crop_to, crop_to)).to(dtype=torch.float)
    outputs = model(x)
    input_names = ["x"]
    outputs = model(x)

    traced = torch.jit.trace(model, x)
    buf = BytesIO()
    torch.jit.save(traced, buf)
    buf.seek(0)

    model = torch.jit.load(buf)

    buf = BytesIO()
    torch.onnx.export(
        model,
        x,
        buf,
        input_names=input_names,
        example_outputs=outputs,
        operator_export_type=torch.onnx.OperatorExportTypes.ONNX_ATEN_FALLBACK,
        opset_version=12,
        do_constant_folding=True
    )
    buf.seek(0)
    onnx_model = onnx.load(buf)

    # Set of optimization passes used in gen-efficientnet-pytorch:
    # https://github.com/rwightman/gen-efficientnet-pytorch/blob/master/onnx_optimize.py#L37
    passes = [
        "eliminate_identity",
        "eliminate_nop_dropout",
        "eliminate_nop_pad",
        "eliminate_nop_transpose",
        "eliminate_unused_initializer",
        "extract_constant_to_initializer",
        "fuse_add_bias_into_conv",
        "fuse_bn_into_conv",
        "fuse_consecutive_concats",
        "fuse_consecutive_reduce_unsqueeze",
        "fuse_consecutive_squeezes",
        "fuse_consecutive_transposes",
        "fuse_pad_into_conv"
    ]

    optimized_model = optimizer.optimize(onnx_model, passes)
    onnx.save(optimized_model, str(export_config.output_path))


if __name__ == '__main__':
    main()
