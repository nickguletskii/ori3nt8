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
