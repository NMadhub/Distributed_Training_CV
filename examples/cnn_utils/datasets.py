"""Functions for getting datasets."""
from __future__ import annotations

import os
from typing import Any

import torch
import torch.distributed as dist
from torchvision import datasets
from torchvision import transforms


def get_cifar(
    args: Any,
) -> tuple[
    torch.utils.data.distributed.DistributedSampler,
    torch.utils.data.DataLoader,
    torch.utils.data.distributed.DistributedSampler,
    torch.utils.data.DataLoader,
]:
    """Get cifar dataset."""
    transform_train = transforms.Compose(
        [
            transforms.RandomCrop(32, padding=4),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize(
                (0.4914, 0.4822, 0.4465),
                (0.2023, 0.1994, 0.2010),
            ),
        ],
    )
    transform_test = transforms.Compose(
        [
            transforms.ToTensor(),
            transforms.Normalize(
                (0.4914, 0.4822, 0.4465),
                (0.2023, 0.1994, 0.2010),
            ),
        ],
    )

    os.makedirs(args.data_dir, exist_ok=True)

    download = True if args.local_rank == 0 else False
    if not download:
        dist.barrier()
    train_dataset = datasets.CIFAR10(
        root=args.data_dir,
        train=True,
        download=download,
        transform=transform_train,
    )
    test_dataset = datasets.CIFAR10(
        root=args.data_dir,
        train=False,
        download=download,
        transform=transform_test,
    )
    if download:
        dist.barrier()

    return make_sampler_and_loader(args, train_dataset, test_dataset)


def get_imagenet(
    args: Any,
) -> tuple[
    torch.utils.data.distributed.DistributedSampler,
    torch.utils.data.DataLoader,
    torch.utils.data.distributed.DistributedSampler,
    torch.utils.data.DataLoader,
]:
    """Get imagenet dataset."""
    train_dataset = datasets.ImageFolder(
        args.train_dir,
        transform=transforms.Compose(
            [
                transforms.RandomResizedCrop(224),
                transforms.RandomHorizontalFlip(),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225],
                ),
            ],
        ),
    )
    val_dataset = datasets.ImageFolder(
        args.val_dir,
        transform=transforms.Compose(
            [
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225],
                ),
            ],
        ),
    )

    return make_sampler_and_loader(args, train_dataset, val_dataset)


def make_sampler_and_loader(
    args: Any,
    train_dataset: torch.utils.data.Dataset,
    val_dataset: torch.utils.data.Dataset,
) -> tuple[
    torch.utils.data.distributed.DistributedSampler,
    torch.utils.data.DataLoader,
    torch.utils.data.distributed.DistributedSampler,
    torch.utils.data.DataLoader,
]:
    """Create sampler and dataloader for train and val datasets."""
    torch.set_num_threads(4)
    kwargs = {'num_workers': 1, 'pin_memory': True} if args.cuda else {}
    kwargs['prefetch_factor'] = 8
    kwargs['persistent_workers'] = True

    train_sampler = torch.utils.data.distributed.DistributedSampler(
        train_dataset,
        num_replicas=dist.get_world_size(),
        rank=dist.get_rank(),
    )
    train_loader = torch.utils.data.DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        sampler=train_sampler,
        **kwargs,
    )
    val_sampler = torch.utils.data.distributed.DistributedSampler(
        val_dataset,
        num_replicas=dist.get_world_size(),
        rank=dist.get_rank(),
    )
    val_loader = torch.utils.data.DataLoader(
        val_dataset,
        batch_size=args.val_batch_size,
        sampler=val_sampler,
        **kwargs,
    )

    return train_sampler, train_loader, val_sampler, val_loader
