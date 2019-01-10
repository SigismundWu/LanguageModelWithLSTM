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
import pandas as pd
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

    def train_the_lstm_model(self):
        model_stand_by = self.deploy_language_model()
        model_ready = LanguageModelPackaging(model_stand_by, self.word_to_index_parameters_set)
        model_ready.train_the_model()
        # if trained with cuda, save it with a name with cuda, else, without cuda, common version
        # torch.save(model_ready, '../configs/trained_model/trained_model_with_cuda.pth')
        torch.save(model_ready, '../configs/trained_model/trained_model_full.pth')

        return model_ready

    def predict_the_probability(self, model_trained=None):
        if model_trained is None:
            print("train a new model and use it")
            model_ready = self.train_the_lstm_model()
        else:
            print("using a trained model")
            model_ready = torch.load(model_trained)

        result = model_ready.prediction_final_assemble()

        return result


if __name__ == "__main__":
    model_ready = LanguageModelDeploy()
    nest_list = model_ready.predict_the_probability()
    print(nest_list)
    final_data_frame = pd.DataFrame(nest_list)
    final_data_frame = final_data_frame.sort_values(by=2, ascending=True)
    final_data_frame.to_csv("../Data/results/normal/final_results.csv", encoding="utf-8")
