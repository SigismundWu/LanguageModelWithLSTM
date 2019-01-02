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

from Data.DataToValidate.DataToValidate import DataToValidate
from PreProcessing.DataCleanComponents import DataCleanComponents
from PreProcessing.RegexPattern import RegexPattern
from LanguageModelCore.PrepareWordVector import PrepareWordVector
from LanguageModelCore.BuildDataWithWord2Vec import BuildDataWithWord2Vec
from PreProcessing.BuildValidateData import BuildValidateData


class LanguageModelPackaging(object):
    def __init__(self, model, word_to_index_parameters_set):
        pd.set_option('max_row', 1500)
        random.seed(0)
        torch.manual_seed(0)
        torch.cuda.manual_seed(0)

        self.model = model
        self.EMBED_SIZE = 128
        self.HIDDEN_SIZE = 1024
        self.NUM_LAYER = 2
        self.LR = 0.001
        self.SEQ_LENGTH = 32  # for bptt
        self.BATCH_SIZE = 32
        self.EPOCH = 10
        self.RESCHEDULED = False
        self.USE_CUDA = torch.cuda.is_available()
        self.build_with_word2vec = BuildDataWithWord2Vec()
        self.pre_clean = PrepareWordVector()
        self.regex_patterns = RegexPattern
        self.word_to_index_parameters_set = word_to_index_parameters_set

    def get_lstm_rnn_parameters(self):
        self.model.init_weight()
        # basically, must with CUDA, otherwise, too, slow
        if self.USE_CUDA:
            # update the model, use cuda
            print("using CUDA")
            self.model = self.model.cuda()
        loss_function = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=self.LR)

        return loss_function, optimizer

    def train_the_model(self):
        train_data = self.build_with_word2vec.batchify(self.word_to_index_parameters_set[0], self.BATCH_SIZE)
        lstm_param_set = self.get_lstm_rnn_parameters()
        loss_function = lstm_param_set[0]
        optimizer = lstm_param_set[1]
        for epoch in range(self.EPOCH):
            total_loss = 0
            losses = []
            hidden = self.model.init_hidden(self.BATCH_SIZE)
            for i, batch in enumerate(
                    self.build_with_word2vec.get_batch(
                        train_data, self.SEQ_LENGTH
                    )
            ):
                inputs, targets = batch
                hidden = self.model.detach_hidden(hidden)
                self.model.zero_grad()
                preds, hidden = self.model(inputs, hidden, False)

                loss = loss_function(preds, targets.view(-1))
                # invalid index of a 0-dim tensor, Use tensor.item() to convert a 0-dim tensor to a Python Number
                # losses.append(loss.data[0])
                losses.append(torch.Tensor.item(loss.data))
                loss.backward()
                torch.nn.utils.clip_grad_norm(self.model.parameters(), 0.5)  # gradient clipping
                optimizer.step()

                if i > 0 and i % 500 == 0:
                    print("[%02d/%d] mean_loss : %0.2f, Perplexity : %0.2f" % (
                    epoch, self.EPOCH, np.mean(losses), np.exp(np.mean(losses))))
                    losses = []

            # learning rate anealing
            if self.RESCHEDULED == False and epoch == self.EPOCH // 2:
                self.LR *= 0.5
                optimizer = optim.Adam(self.model.parameters(), lr=self.LR)
                # update the param
                self.RESCHEDULED = True

        return self.model

    def prediction_preparation(self):
        validate_data_instance = BuildValidateData()
        sentences = validate_data_instance.read_data()
        sentences_clean = []
        for itm in sentences:
            itm = self.pre_clean.pre_data_clean(itm, self.regex_patterns.re_first)
            itm = self.pre_clean.pre_data_clean(itm, self.regex_patterns.re_dict)
            itm = self.pre_clean.pre_data_clean(itm, self.regex_patterns.re_symb)
            itm = self.pre_clean.pre_data_clean(itm, self.regex_patterns.re_dict)
            itm = self.pre_clean.pre_data_clean(itm, self.regex_patterns.re_number)
            sentences_clean.append(itm)

        sentences_proc = []
        for itm in sentences_clean:
            no = len(itm.split())
            itm = itm + ' ' + '. ' * (self.SEQ_LENGTH - no - 1) + '.'
            sentences_proc.append(itm.strip())

        position = []
        for itm in sentences_proc:
            position.append(itm.split().index('.') - 1)

        return sentences_proc, position

    def predict_the_probability(self):
        continue_prob = 0.0
        # predict the probability between the words in sentences
        sentences_param_set = self.prediction_preparation()
        sentences_proc = sentences_param_set[0]
        position = sentences_param_set[1]
        word2index = self.word_to_index_parameters_set[1]
        for k, itm in enumerate(sentences_proc):
            print(itm.replace('.', ''))

            test_data, _ = self.build_with_word2vec.prepare_ptb_dataset(itm, word2index)
            test_data = self.build_with_word2vec.batchify(test_data, self.BATCH_SIZE // self.BATCH_SIZE)

            total_loss = 0
            hidden = self.model.init_hidden(self.BATCH_SIZE // self.BATCH_SIZE)
            for i, batch in enumerate(self.build_with_word2vec.get_batch(test_data, self.SEQ_LENGTH)):
                inputs, targets = batch
                hidden = self.model.detach_hidden(hidden)
                self.model.zero_grad()
                preds, hidden = self.model(inputs, hidden)

                continue_prob = 0
                for i in range(self.SEQ_LENGTH):
                    if i < position[k]:
                        y_prob = preds.data[i].cpu().numpy()
                        y_prob = np.exp(y_prob)
                        y_prob = y_prob[y_prob >= 0]
                        y_prob = y_prob / np.sum(y_prob)
                        y_index = list(np.nonzero(y_prob >= 0))
                        y_index = y_index[0]
                        res = dict(list(zip(list(y_index), list(y_prob))))
                        next_word_prob = math.log(res[int(targets[0][i].data)], 10)
                        print(next_word_prob)
                        continue_prob += next_word_prob
                print('total_continue_prob:', continue_prob)

        return continue_prob
