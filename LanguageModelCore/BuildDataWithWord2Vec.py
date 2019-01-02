# -*- coding:utf-8 -*-
import logging
from collections import Counter, OrderedDict
import torch
import torch.nn as nn
from torch.autograd import Variable
import torch.optim as optim
import torch.nn.functional as F
import nltk
import random
import numpy as np
import nltk
import math
import string
import re
import os
import time
from collections import OrderedDict
import pandas as pd
import multiprocessing as mp

from LanguageModelCore.PrepareWordVector import PrepareWordVector


class BuildDataWithWord2Vec(PrepareWordVector):
    def __init__(self):
        super(BuildDataWithWord2Vec).__init__()
        # with a single GPU to train, if got better machine with more than 1 GPU, fix this init, just a check
        self.USE_CUDA = torch.cuda.is_available()
        # self.gpus is a list, depends on how many gpus you have, usually one, mark it 0
        # if without CUDA support, do not use this
        # self.gpus = [0]
        # self.set_gpu = torch.cuda.set_device(self.gpus[0])
        # sequence of the set: train_data, word2index, index2word
        self.path = "../configs/LanguageModelParameters/"
        prepare_inst = PrepareWordVector()
        self.texts = prepare_inst.recursive_find_all_text(prepare_inst.mp_based_the_clean_engine_core())
        self.EMBED_SIZE = 128


    @staticmethod
    def flatten_sublists(lst):
        # flatten = lambda l: [item for sublist in l for item in sublist] , not suggested to value a lambda
        flattened_list = list()
        for sublists in lst:
            for item in sublists:
                flattened_list.append(item)

        return flattened_list

    def prepare_sequence(self, seq, to_index):
        idxs = list(map(lambda w: to_index[w] if to_index.get(w) is not None else to_index["<unk>"], seq))

        return torch.LongTensor(idxs)

    def prepare_ptb_dataset(self, texts, word2index=None):
        corpus = [texts]
        print(corpus)
        corpus = self.flatten_sublists([co.strip().split() for co in corpus])

        if word2index is None:
            vocab = list(set(corpus))
            word2index = {'<unk>': 0}
            for vo in vocab:
                if word2index.get(vo) is None:
                    word2index[vo] = len(word2index)

        return self.prepare_sequence(corpus, word2index), word2index

    def batchify(self, data, bsz):
        # Work out how cleanly we can divide the dataset into bsz parts.
        nbatch = data.size(0) // bsz
        # Trim off any extra elements that wouldn't cleanly fit (remainders).
        data = data.narrow(0, 0, nbatch * bsz)
        # Evenly divide the data across the bsz batches.
        data = data.view(bsz, -1).contiguous()
        if self.USE_CUDA:
            data = data.cuda()
        return data

    @classmethod
    def get_batch(cls, data, seq_length):
        size = data.size(1) - seq_length
        if size < 1:
            size = 1
        for i in range(0, size, seq_length):
            inputs = Variable(data[:, i: i + seq_length])
            targets = Variable(data[:, (i + 1): (i + 1) + seq_length].contiguous())
            yield (inputs, targets)

    def word_to_index(self):
        train_data, word2index = self.prepare_ptb_dataset(self.texts)
        index2word = {v: k for k, v in word2index.items()}

        # save word2index
        df_word2index = pd.DataFrame(columns=['keys', 'values'])
        df_word2index['keys'] = list(word2index.keys())
        df_word2index['values'] = list(word2index.values())
        df_word2index = df_word2index.sort_values(by=['values'], ascending=1)
        df_word2index.to_csv(self.path + 'word2index.csv', index=False)

        return train_data, word2index, index2word

    def pretrained_weight(self):
        # pretrained_weight
        # index2word, meanwhile the third parameter of the return of the word_to_index
        word_to_index_parameters_set = self.word_to_index()
        wd_list = list(word_to_index_parameters_set[2].values())
        pretrained_weight = list()
        trained_model = self.get_the_model_with_gensim()

        for itm in wd_list:
            try:
                pretrained_weight.append(trained_model[itm])
            except Exception as e:
                pretrained_weight.append(np.random.random(self.EMBED_SIZE) * 2 - 1)
                logging.exception(e)

        pretrained_weight = np.array(pretrained_weight)
        print(pretrained_weight.shape)

        # save pretrained_weight
        df_pretrained_weight = pd.DataFrame(pretrained_weight)
        df_pretrained_weight.to_csv(self.path + 'pretrained_weight.csv', index=False)

        return pretrained_weight


if __name__ == "__main__":
    inst = BuildDataWithWord2Vec()
    print(inst.word_to_index()[0])
    print(len(inst.word_to_index()[1]))
