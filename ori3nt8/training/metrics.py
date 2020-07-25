import torch


def calculate_accuracy(output: torch.Tensor, target: torch.Tensor):
    return (output.argmax(dim=-1) == target).sum().float() / target.shape[0]
