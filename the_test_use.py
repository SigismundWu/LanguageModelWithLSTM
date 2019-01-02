# -*- coding:utf-8 -*-
import asyncio
import sys
import multiprocessing

import PreProcessing
import torch


if __name__ == "__main__":
    device = torch.device("cuda: 0” if torch.cuda.is_available() else “cpu")
    print(device)
    torch.Tensor.item()