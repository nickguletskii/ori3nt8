# Development

Ori3nt8 requires Python 3.7 or later.

## UI Development

### Prerequisites

Create and activate a Python 3.7 virtual environment, then install the requirements:

```shell script
pip install --upgrade pip setuptools
pip install -r requirements.txt
pip install torch==1.5.1+cpu torchvision==0.6.1+cpu -f https://download.pytorch.org/whl/torch_stable.html
```

Retrieve the pretrained neural network:

```shell script
export MC_HOST_ng_anon=https://minio.centos2.nickguletskii.com/
mkdir downloads
wget -O downloads/mc -c https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x downloads/mc
./downloads/mc cp ng_anon/ori3nt8-models/network.onnx resources/network.onnx
```

### Compiling designer files

To compile the Qt designer files, run `ori3nt8.gui.utils.ui_file`: 
```shell script
python -m ori3nt8.gui.utils.ui_file
```

During development, the UI files should be automatically compiled when starting the GUI.

### Launching the GUI during development

To launch the GUI, simply run

```shell script
python -m ori3nt8.gui.main
```


## Training

### Prerequisites
Training requires [CUDA 10.2](https://docs.nvidia.com/cuda/) and a separate virtual environment with CUDA-aware PyTorch. 
You can install the dependencies by running

```shell script
pip install -r requirements_gpu.txt
```

You will also need to install [Apex](https://github.com/NVIDIA/apex) if you intend to make use of mixed precision 
training.

### Hyperparameters

The training hyperparameters can be adjusted in `configs/default.toml`. For more information, please refer to the config
file and classes decorated with `@configuration`.

The default hyperparameters are tuned for mixed-precision training on a single NVIDIA RTX 2070 (with 8 gigabytes of 
VRAM).

### Running the training procedure

The training script requires two directories of correctly oriented images: one for training and one for validation.

```shell script
python -m ori3nt8.training.main \
       --Ddatasets.training.path [PATH_TO_TRAINING_SET] \
       --Ddatasets.validation.path [PATH_TO_VALIDATION_SET] \
       --config-path=configs/default.toml
```

The provided weights were obtained by training a pretrained efficientnet_b1 model on the images present in
the [MS COCO 2017 dataset](https://cocodataset.org).