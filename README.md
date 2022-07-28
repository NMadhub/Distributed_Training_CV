## Requirements
This repo only requires PyTorch 1.8 or later. The example scripts have additional requirements defined in examples/requirements.txt.

## Installation
First, Clone this repo and go inside the directory
```
$ git clone https://github.com/NMadhub/Distributed_Training_CV.git
$ cd Distributed_Training_CV
$ pip3 install .  
```
# Training Example

Cifar-10 distributed training example.

## Requirements

The provided example training scripts have additional package requirements defined in `examples/requirements.txt`.

```
$ pip3 install -r examples/requirements.txt
```

## Usage

Note: these examples use the `torchrun` launcher which is only available in PyTorch 1.10 and later.
For PyTorch 1.9, use `python -m torch.distributed.run` and for PyTorch 1.8, use `python -m torch.distributed.launch`.


#### Single Node, Multi-GPU
```
$ torchrun --standalone --nnodes 1 --nproc_per_node=[NGPUS] \
      examples/torch_{cifar10,imagenet}_resnet.py [ARGS]

$ python3 -m torch.distributed.launch --nnodes 1 --nproc_per_node=[NGPUS] /home/ninadm/my_codes/ptl/kfac-pytorch/examples/torch_cifar10_resnet.py --batch-size 32 --val-batch-size 32
```

#### Multi-Node, Multi-GPU
On each node, run:
```
$ torchrun --nnodes=[NNODES] --nproc_per_node=[NGPUS] --rdzv_backend=c10d --rdzv_endpoint=[HOSTADDR] \
      examples/torch_{cifar10,imagenet}_resnet.py [ARGS]
      
$ python3 -m torch.distributed.launch --nnodes=[NNODES] --nproc_per_node=[NGPUS] --rdzv_backend=c10d --rdzv_endpoint=[HOSTADDR] \
      examples/torch_{cifar10,imagenet}_resnet.py --batch-size 32 --val-batch-size 32
```

The full list of arguments can be found with the `--help` argument.
E.g., `python3 examples/torch_cifar10_resnet.py --help`.
