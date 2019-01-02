# -*- coding:utf-8 -*-
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


class LanguageModelTorch(nn.Module):
    def __init__(self, vocab_size, embedding_size, hidden_size,
                 pretrained_weight, n_layers=1, dropout_p=0.25):
        pd.set_option('max_row', 1500)
        random.seed(0)
        torch.manual_seed(0)
        torch.cuda.manual_seed(0)
        super(LanguageModelTorch, self).__init__()
        self.n_layers = n_layers
        self.hidden_size = hidden_size
        self.embed = nn.Embedding(vocab_size, embedding_size)
        self.rnn = nn.LSTM(embedding_size, hidden_size, n_layers, batch_first=True)
        self.linear = nn.Linear(hidden_size, vocab_size)
        self.dropout = nn.Dropout(dropout_p)
        self.pretrained_weight = pretrained_weight
        self.USE_CUDA = torch.cuda.is_available()

    def init_weight(self):
        self.embed.weight.data.copy_(torch.from_numpy(self.pretrained_weight))
        self.linear.weight = nn.init.xavier_uniform(self.linear.weight)
        self.linear.bias.data.fill_(0)

    def init_hidden(self, batch_size):
        hidden = Variable(torch.zeros(self.n_layers, batch_size, self.hidden_size))
        context = Variable(torch.zeros(self.n_layers, batch_size, self.hidden_size))
        return (hidden.cuda(), context.cuda()) if self.USE_CUDA else (hidden, context)

    def detach_hidden(self, hiddens):
        return tuple([hidden.detach() for hidden in hiddens])

    def forward(self, inputs, hidden, is_training=False):
        embeds = self.embed(inputs)
        if is_training:
            embeds = self.dropout(embeds)
        out, hidden = self.rnn(embeds, hidden)
        return self.linear(out.contiguous().view(out.size(0) * out.size(1), -1)), hidden
