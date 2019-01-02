# -*- coding:utf-8 -*-
import asyncio
import sys
import multiprocessing

import PreProcessing
import torch
from gensim.models import word2vec


if __name__ == "__main__":
    device = torch.device("cuda: 0” if torch.cuda.is_available() else “cpu")
    print(device)
    print(word2vec.FAST_VERSION)
