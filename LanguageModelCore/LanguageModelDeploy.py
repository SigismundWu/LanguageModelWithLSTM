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
import multiprocessing as mp

from PreProcessing.RegexPattern import RegexPattern
from LanguageModelCore.LanguageModelPackaging import LanguageModelPackaging
from LanguageModelCore.LanguageModelTorch import LanguageModelTorch
from LanguageModelCore.BuildDataWithWord2Vec import BuildDataWithWord2Vec
from LanguageModelCore.PrepareWordVector import PrepareWordVector

class LanguageModelDeploy(object):
    def __init__(self):
        self.EMBED_SIZE = 128
        self.HIDDEN_SIZE = 1024
        self.NUM_LAYER = 2
        self.LR = 0.001
        self.SEQ_LENGTH = 32  # for bptt
        self.BATCH_SIZE = 32
        self.EPOCH = 10
        self.RESCHEDULED = False
        self.build_with_word2vec = BuildDataWithWord2Vec()
        self.pre_clean = PrepareWordVector()
        self.regex_patterns = RegexPattern
        self.word_to_index_parameters_set = self.build_with_word2vec.word_to_index()
        self.vocab = self.word_to_index_parameters_set[1]

        self.pretrained_weight = self.build_with_word2vec.pretrained_weight()
        self.drop_rate = 0.3

    def deploy_language_model(self):
        # the
        print(self.vocab)
        model = LanguageModelTorch(
            len(self.vocab), self.EMBED_SIZE, self.HIDDEN_SIZE,
            self.pretrained_weight, self.NUM_LAYER, self.drop_rate
        )

        return model


if __name__ == "__main__":
    device = torch.device("cuda: 0” if torch.cuda.is_available() else “cpu")
    instance = LanguageModelDeploy()
    model = instance.deploy_language_model()
    prediction_tool = LanguageModelPackaging(model)
    prediction_tool.train_the_model()
    prob = prediction_tool.predict_the_probability()
    print(prob)
