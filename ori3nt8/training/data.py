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

import random

import torch
from torchvision.datasets import VisionDataset
from torchvision.datasets.folder import default_loader


class ImageFolderDataset(VisionDataset):
    def __init__(self, root, transform):
        super().__init__(root)
        self.paths = sorted(root.glob("**/*.jpg"), key=lambda x: str(x))
        self.transform = transform

    def __getitem__(self, index):
        res = default_loader(str(self.paths[index])), 0
        if self.transform is not None:
            res = self.transform(res)
        return res

    def __len__(self):
        return len(self.paths)


class ApplyTransformToImage(object):
    def __init__(self, image_transform):
        self.image_transform = image_transform

    def __call__(self, arg):
        (x, *rest) = arg
        return (self.image_transform(x), *rest)


class RandomRotateTransform(object):
    def __call__(self, arg):
        image, label = arg
        t = random.randint(0, 3)
        label = (label + t) % 4
        image = torch.rot90(image, t, dims=(1, 2))
        return image, label


class RotateNTimesTransform(object):
    def __init__(self, rotate_n_times: int):
        self.rotate_n_times = rotate_n_times

    def __call__(self, arg):
        image, label = arg
        label = (label + self.rotate_n_times) % 4
        image = torch.rot90(image, self.rotate_n_times, dims=(1, 2))
        return image, label
