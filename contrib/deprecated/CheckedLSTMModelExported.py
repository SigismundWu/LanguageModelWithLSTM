
# coding: utf-8

# In[1]:


import torch
import torch.nn as nn
from torch.autograd import Variable
import torch.optim as optim
import torch.nn.functional as F
import nltk
import random
import numpy as np
from collections import Counter, OrderedDict
import nltk
import math
import string
import re
import os
import time
from collections import OrderedDict
import pandas as pd

pd.set_option('max_row', 1500)
random.seed(0)
torch.manual_seed(0)
torch.cuda.manual_seed(0)


# In[3]:


def clean(texts, re_lists, final=False):
    items = re_lists.keys()
    for i, itm in enumerate(items):
        start = time.time()
        texts = re.sub(itm, re_lists[itm], texts)
        end = time.time()
        seconds = end - start
        print(i, 'finished')
        if seconds > 1:
            print(itm)
            print(seconds, 'seconds')
    if final:
        texts = ' '.join(texts.split())
    return texts


# In[5]:


path = '/Users/roger.zhou/Downloads/Project_Gutenberg/'

subfolder = 'c'
file_name = []
texts = []
k = 0
for parent, subfolders, files in os.walk(path + subfolder + '/'):
    for i, unt in enumerate(files):
        unt = os.path.join(parent, unt)
        if (unt.find('DS_Store') < 0) & (os.path.getsize(unt) > 0):
            file_name.append(unt)
            if i % 1000 == 0:
                print('processing task:', i)
            try:
                with open(unt, 'r', encoding='utf-8') as f:
                    for line in f:
                        texts.append(line)
                f.close()
            except Exception:
                print(unt, 'failed')
                k += 1
print('processing finished...')
texts = ' '.join(texts)
print('total files:', len(file_name))
print('failed:', k)
print(texts[0: 1500])


# In[8]:


# re_lists
re_first = [
           ['\<', ''], ['\>', ''], 
           ]
re_first = OrderedDict(re_first)

re_dict = [
           # 无意义的标题或词汇行
#            ['\n.{1,300}?\.\n', ''], ['\\bclick to see content\s*:\s*[\w_]\\b', ''], 
#            ['\\bfollow\s[\w\s]+on\stwitter\s@\w+BBC\\b', ''], ['\\b\d{1,2}\.\s', '. '], 
#            ['\\bclick to see content:\s+', ''], ['&amp;', ' '], ['&nbsp;', ' '], 
           ['\\bby.{2,40}?\d{1,2}\sjanuary\s\d{4}|\\bby.{2,40}?\d{1,2}\sfebruary\s\d{4}|\\bby.{2,40}?\d{1,2}\smarch\s\d{4}|\\bby.{2,40}?\d{1,2}\sapril\s\d{4}|\\bby.{2,40}?\d{1,2}\smay\s\d{4}|\\bby.{2,40}?\d{1,2}\sjune\s\d{4}|\\bby.{2,40}?\d{1,2}\sjuly\s\d{4}|\\bby.{2,40}?\d{1,2}\saugust\s\d{4}|\\bby.{2,40}?\d{1,2}\sseptember\s\d{4}|\\bby.{2,40}?\d{1,2}\soctober\s\d{4}|\\bby.{2,40}?\d{1,2}\snovember\s\d{4}|\\bby.{2,40}?\d{1,2}\sdecember\s\d{4}|', ''], 
           # 缩写
           ['\\bd\.c\.', 'dc'], ['\\bu\.s\.', 'america'], ['\\bu\.n\.', 'un'], 
           ['\\bdr\.', 'dr'], ['\\bmr\.', 'mr'], ['\\bms\.', 'ms'], 
           ['\\b(\w\s+\.){1, 4}', '<abbr> '], ['\\bpres\.', 'president'], 
           ['\\bjan\.|\\bjan\\b', 'january'], ['\\bfeb\.|\\bfeb\\b', 'february'], 
           ['\\bmar\.|\\bmar\\b', 'march'], ['\\bapr\.|\\bapr\\b', 'april'], 
           ['\\bjun\.|\\bjun\\b', 'june'], ['\\bjul\.|\\bjul\\b', 'july'], 
           ['\\baug\.|\\baug\\b', 'august'], ['\\bsep\.|\\bsep\\b', 'september'], 
           ['\\boct\.|\\boct\\b', 'october'], ['\\bnov\.|\\bnov\\b', 'november'], 
           ['\\bdec\.|\\bdec\\b', 'december'], 
           ['\\bsec\.', 'secretary'], 
           # 简写
           ['(?<=\\bit)[’\']s\\b|(?<=\\bhe)[’\']s\\b|(?<=\\bshe)[’\']s\\b|(?<=\\bthat)[’\']s\\b|(?<=\\bthis)[’\']s\\b|(?<=\\bthere)[’\']s\\b|(?<=\\bhere)[’\']s\\b', ' is'], 
           ['(?<=[a-zA-Z])[’\']re\\b', ' are'], ['(?<=[a-zA-Z])[’\']d\\b', ' would'], 
           ['(?<=[a-zA-Z])[’\']ve\\b', 'have'], ["(?<=[a-zA-Z])n[’\']t\\b", ' not'], 
           ['(?<=[a-zA-Z])[’\']m\\b', ' am'],  ['[’\']ll\\b', ' will'], 
           # 货币
           ['[\$￡]*\s*\d[\s,\d\.]{0,10}\s*bn*\\b', '<money> billion'], 
           ['[\$￡]\s*\d[\s,\d\.]{0,10}\s*m\\b', '<money> million'], 
           ['[\$￡]*\s*\d[\s,\d\.]{0,10}\s*tr*n\\b|[\$￡]*\s*\d[\s,\d\.]{0,10}\s*tr\\b', '<money> trillion'], 
           ['\$￡]\s*\d[\s,\d\.]{0,10}\s*k\\b', '<money> thousand'], 
           ['[\$￡]\s*\d[\s,\d\.]{0,10}\\b', '<money> '], # $10
           # date
           # month-day-year
           ['\\bjanuary[,\s-]+\d{1,2}[,\s-]+\d{4}\\b|\\bfebruary[,\s-]+\d{1,2}[,\s-]+\d{4}\\b|\\bmarch[,\s-]+\d{1,2}[,\s-]+\d{4}\\b|\\bapril[,\s-]+\d{1,2}[,\s-]+\d{4}\\b|\\bmay[,\s-]+\d{1,2}[,\s-]+\d{4}\\b|\\bjune[,\s-]+\d{1,2}[,\s-]+\d{4}\\b|\\bjuly[,\s-]+\d{1,2}[,\s-]+\d{4}\\b|\\baugust[,\s-]+\d{1,2}[,\s-]+\d{4}\\b|\\bseptember[,\s-]+\d{1,2}[,\s-]+\d{4}\\b|\\boctober[,\s-]+\d{1,2}[,\s-]+\d{4}\\b|\\bnovember[,\s-]+\d{1,2}[,\s-]+\d{4}\\b|\\bdecember[,\s-]+\d{1,2}[,\s-]+\d{4}\\b', '<month> <day> <year>'], # May 15, 1864
           ['\\b\d{1,2}\s+january\s+\d{4}\\b|\\b\d{1,2}\s+february\s+\d{4}\\b|\\b\d{1,2}\s+march\s+\d{4}\\b|\\b\d{1,2}\s+april\s+\d{4}\\b|\\b\d{1,2}\s+may\s+\d{4}\\b|\\b\d{1,2}\s+june\s+\d{4}\\b|\\b\d{1,2}\s+july\s+\d{4}\\b|\\b\d{1,2}\s+august\s+\d{4}\\b|\\b\d{1,2}\s+september\s+\d{4}\\b|\\b\d{1,2}\s+october\s+\d{4}\\b|\\b\d{1,2}\s+november\s+\d{4}\\b|\\b\d{1,2}\s+december\s+\d{4}\\b', '<day> <month> <year>'], 
           # month-year
           ['\\bjanuary\s+\d{4}\\b|\\bfebruary\s+\d{4}\\b|\\bmarch\s+\d{4}\\b|\\bapril\s+\d{4}\\b|\\bmay\s+\d{4}\\b|\\bjune\s+\d{4}\\b|\\bjuly\s+\d{4}\\b|\\baugust\s+\d{4}\\b|\\bseptember\s+\d{4}\\b|\\boctober\s+\d{4}|november\s+\d{4}\\b|\\bdecember\s+\d{4}\\b', '<month> <year>'], # march 2017
           # month-day
           ['\\bjanuary\s+\d{1,2}\\b|\\bfebruary\s+\d{1,2}\\b|\\bmarch\s+\d{1,2}\\b|\\bapril\s+\d{1,2}\\b|\\bmay\s+\d{1,2}\\b|\\bjune\s+\d{1,2}\\b|\\bjuly\s+\d{1,2}\\b|\\baugust\s+\d{1,2}\\b|\\bseptember\s+\d{1,2}\\b|\\boctober\s+\d{1,2}|november\s+\d{1,2}\\b|\\bdecember\s+\d{1,2}\\b', '<month> <day>'], 
           # day-month
           ['\\b\d{1,2}\s+junuary\\b|\\b\d{1,2}\s+february\\b|\\b\d{1,2}\s+march\\b|\\b\d{1,2}\s+april\\b|\\b\d{1,2}\s+may\\b|\\b\d{1,2}\s+june\\b|\\b\d{1,2}\s+july\\b|\\b\d{1,2}\s+august\\b|\\b\d{1,2}\s+september\\b|\\b\d{1,2}\s+october\\b|\\b\d{1,2}\s+november\\b|\\b\d{1,2}\s+december\\b', '<day> <month>'], 
           # generation
           ['\\b\d{4}s\s+&\s+\d{2,4}s\\b|\\b\d{4}s\s+and\s+\d{2,4}s\\b|\\b\d{4}s\s+&\s+early\s+\d{2,4}s\\b|\\b\d{4}s\s+&\s+late\d{2,4}s\\b|\\b\d{4}s\s+and\s+early\d{2,4}s\\b|\\b\d{4}s\s+and\s+late\d{2,4}s\\b', '<generation>'], 
           ['\\bearly\s+\d{2,4}s\\b|\\blate\s+\d{2,4}s\\b', '<generation>'], 
           ['\\b\d{2,4}s\\b', '<generation>'], 
           # year
           ['\\byear\s+\d{4}[,\s-]+year\s+\d{4}\\b|\\byear\s+\d{4}[,\s-]+\d{4}\\b', '<year>'], # year 2017-2018
           ['\\byear[,\s-]+\d{4}\\b', '<year>'], # year 2017
           ['\\bby\s\d{4}-\d{2,4}\\b|\\bfrom\s\d{4}-\d{2,4}\\b|\\bduring\s\d{4}-\d{2,4}\\b', '<year>'], # by 2017-19
           ['(?<=\\bafter\sthe\s)d{4}\\b|(?<=\\bafter\s)\d{4}\\b|(?<=\\bbefore\sthe\s)d{4}\\b|(?<=\\bbefore\s)\d{4}\\b', '<year>'], 
           ['(?<=\\bpost)[,\s-]+\d{4}\\b|(?<=\\bpre)[,\s-]+\d{4}\\b|(?<=\\blate)[,\s-]+\d{4}\\b|(?<=\\bearly)[,\s-]+\d{4}\\b', '<year>'], # post 2017
           ['(?<=\\bby\s)\d{4}\\b|(?<=\\bof\s)\d{4}\\b|(?<=\\bin\s)\d{4}\\b|(?<=\\bsince\s)\d{4}\\b|(?<=\\buntil\s)\d{4}\\b|(?<=\\blast\s)\d{4}\\b|(?<=\\bbetween\s)\d{4}\s+&\s+\d{4}\\b|(?<=\\bbetween\s)\d{4}\s+and\s+\d{4}\\b', '<year>'], 
           ['(?<=\\bin\s)t*h*e*\s+[12]\d{3}\\b|(?<=\\buntil\s)t*h*e*\s+[12]\d{3}\\b|(?<=\\bsince\s)t*h*e*\s+[12]\d{3}\\b', '<year>'], #  in 2017
           # month
           ['\\bjanuary\\b|\\bfebruary\\b|march\\b|\\bapril\\b|\\bjune\\b|\\bjuly\\b|\\baugust\\b|\\bseptember|\\boctober\\b|\\bnovember\\b|\\bdecember\\b', '<month>'], # march
           # 百分比
           ['%', ' percent'], 
           # 单位
           ['\\b\d{1,4}x\d{1,4}\s*m\\b', '<noxno> m'], 
           ['\\b\d[\d,\.]{0,10}sq\s*feet\\b', '<no> sq feet'], ['\\b\d[\d,\.]{0,10}hrs*\\b', '<no> hour'], 
#            ['\\b\d[\d,\.]{0,10}mmhg\\b', '<no> mmhg'], ['\\b\d[\d,\.]{0,10}mbps\s\\b', '<no> mbps'], 
           ['\\b\d[\d,\.]{0,10}gbps\\b', '<no> gbps'], ['\\b\d[\d,\.]{0,10}sq\s*rt\\b', '<no> sqft'], 
           ['\\b\d[\d,\.]{0,10}gbz\\b', '<no> gbz'], ['\\b\d[\d,\.]{0,10}sq\s*m\\b', '<no> sqm'],
#            ['\\b\d[\d,\.]{0,10}kwh\\b', '<no> kwh'], ['\\b\d[\d,\.]{0,10}sq\s*km\\b', '<no> sqkm'],
#            ['\\b\d[\d,\.]{0,10}ers\\b', '<no> ers'], ['\\b\d[\d,\.]{0,10}lbn\\b', '<no> lbn'], 
#            ['\\b\d[\d,\.]{0,10}ins\\b', '<no> ins'], ['\\b\d[\d,\.]{0,10}mph\\b', '<no> mph'], 
#            ['\\b\d[\d,\.]{0,10}msv\\b', '<no> msv'], ['\\b\d[\d,\.]{0,10}kmh\\b', '<no> kmh'], 
#            ['\\b\d[\d,\.]{0,10}pph\\b', '<no> pph'], ['\\b\d[\d,\.]{0,10}lbs\\b', '<no> lbs'], 
#            ['\\b\d[\d,\.]{0,10}mdb\\b', '<no> mdb'], ['\\b\d[\d,\.]{0,10}mmt\\b', '<no> mmt'], 
#            ['\\b\d[\d,\.]{0,10}mg\\b', '<no> mg'], ['\\b\d[\d,\.]{0,10}kb\\b', '<no> kb'], 
#            ['\\b\d[\d,\.]{0,10}kw\\b', '<no> kw'], ['\\b\d[\d,\.]{0,10}gb\\b', '<no> gb'], 
           ['\\b\d[\d,\.]{0,10}km\\b', '<no> km'], ['\\b\d[\d,\.]{0,10}ft\\b', '<no> ft'], 
           ['\\b\d[\d,\.]{0,10}kg\\b', '<no> kg'], ['\\b\d[\d,\.]{0,10}ml\\b', '<no> ml'], 
#            ['\\b\d[\d,\.]{0,10}cm\\b', '<no> cms'], ['\\b\d[\d,\.]{0,10}lb\\b', '<no> lb'], 
#            ['\\b\d[\d,\.]{0,10}in\\b', '<no> in'], ['\\b\d[\d,\.]{0,10}tb\\b', '<no> tb'], 
#            ['\\b\d[\d,\.]{0,10}cc\\b', '<no> cc'], 
           ['\\b\d[\d,\.]{0,10}mm\\b', '<no> mm'], 
#            ['\\b\d[\d,\.]{0,10}mw\\b', '<no> mw'], ['\\b\d[\d,\.]{0,10}nm\\b', '<no> nm'], 
           ['\\b\d[\d,\.]{0,10}m\\b', '<no> m'], 
#            ['\\b\d[\d,\.]{0,10}c\\b', '<no> c'], 
#            ['\\b\d[\d,\.]{0,10}f\\b', '<no> f'], ['\\b\d[\d,\.]{0,10}p\\b', '<no> p'], 
#            ['\\b\d[\d,\.]{0,10}g\\b', '<no> g'], ['\\b\d[\d,\.]{0,10}v\\b', '<no> v'], 
           # 时间
           ['\\b\d{1,2}\s*:\s*\d{1,2}GMT\\b', '<time> GMT'], 
           ['\\b\d{1,2}\s*:\s*\d{1,2}\\b', '<time>'], # 7:05
           ['\\b\d[:\d]*[ap]m\\b', '<time>'], 
           # 邮箱
#            ['\\b[\w\d_\.]+@[\w\d_\.]+\\b', '<mail address>'], 
           # 其他
           ['\\b3\s*-\s*d\\b', '3d'], ['\.\.\.', ' '], ['wi - fi', 'wifi'], 
           # 网址
#            ['\\bh*t*t*p*:*/*/*www\.[\w\d\.]+\\b', '<url>'], 
#            ['\s[\w\d\.]+com\\b|[\w\d\.]+cn\\b', ' <url>'], 
           # 电话
#            ['\+\s*\d{1,4}[\d\(\)\s-]{4,12}\\b', '<tele no>'], 
           # 型号
#            ['\\bmi\d{1,4}\\b|\\bitv\d{1,4}\\b|\\b\ds\\b|\\bp\d{1,4}\\b', '<brand type>'], 
#            ['\\bmate\d{1,4}\\b|\\bps\d{1,4}\\b', '<brand type>'], 
           # 还原
#            ['\\bh1[\s-]*b\\b', 'h1-b'], 
           ['<money> million <money> million', '<money> million'], 
           ['\.\s\.', '.'], 
#            ['h & m', 'h&m'], 
           ]
re_dict = OrderedDict(re_dict)

re_symb = [
          # 符号
          ['‘', '\''], ['//', ''], ['”', ' " '], ['，', ' , '], ['：', ' : '], ['…', ''], ['–', ' - '], 
          ['-[\s-]+-', '-'], ['"', ' " '], ['\#', ' # '], ['\%', ' % '], ['&', ' & '], ['\!', ' . '], 
          ['\'', ' \' '], ['\(', ''], ['\)', ''], ['\*', ' * '], ['\+', ' + '], [',', ' , '], 
          ['-', ' - '], ['\.', ' . '], ['/', ' / '], [':', ' : '], [';', ' ; '], ['“', ' " '], 
          ['=', ' = '], ['\?', ' . '], ['@', ' @ '], ['\[', ''], ['\]', ''], ['\$', ' $ '], 
          ['\^', ' ^ '], ['_', ' _ '], ['`', ' ` '], ['\{', ' { '], ['\|', ' | '], ['\}', ' } '], 
          ['—', ' — '], ['\s+', ' '], ['’', " ' "], ["' s", "'s"], ["\\'s", "'s"]
          ]
re_symb = OrderedDict(re_symb)

re_number = [
            # 数字
            ['\\b\d+x\d+\\b', '<no>x<no>'], 
            ['\\b\d+rd|\d+th|\d+st\\b|\\b\d+nd\\b', '<num>'], # 23rd
            ['\\b\d[\d,\s\.]+\\b', '<no> '], # 300
            ['\\b\d\\b', '<no>'] # 单独一个数字: 5
            ]
re_number = OrderedDict(re_number)


# In[9]:


pattern = re.compile('.{10}\d+.{10}', re.I)
res = re.findall(pattern, texts)
print('dirty data before cleaning:', len(res))

# data cleaning
texts = clean(texts, re_first)
print('re_first_finished')
texts = clean(texts, re_dict)
print('re_dict_finished')
texts = clean(texts, re_symb)
print('re_symb_finished')
texts = clean(texts, re_dict)
# print('re_dict_finished')
texts = clean(texts, re_number, final=True)
print('re_number_finished')

texts = texts.lower().strip()
print(texts[1000: 2000])

# dirty data size after cleaning
pattern = re.compile('.{50}\d+.{50}', re.I)
res = re.findall(pattern, texts)
print('dirty data after cleaning:', len(res))

res[2000: 3000]


# In[8]:


# dirty data size before cleaning
pattern = re.compile('.{10}\d+.{10}', re.I)
res = re.findall(pattern, texts)
print('dirty data before cleaning:', len(res))

# data cleaning
texts = clean(texts, re_first)
print('re_first_finished')
texts = clean(texts, re_dict)
print('re_dict_finished')
texts = clean(texts, re_symb)
print('re_symb_finished')
# texts = clean(texts, re_dict)
# print('re_dict_finished')
texts = clean(texts, re_number, final=True)
print('re_number_finished')

texts = texts.lower().strip()
print(texts[1000: 2000])

# dirty data size after cleaning
pattern = re.compile('.{50}\d+.{50}', re.I)
res = re.findall(pattern, texts)
print('dirty data after cleaning:', len(res))
res[2000: 3000]


# In[10]:


import gensim
import logging
from gensim.models import word2vec
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


# In[11]:


EMBED_SIZE = 128
HIDDEN_SIZE = 1024
NUM_LAYER = 1
LR = 0.001
SEQ_LENGTH = 32 # for bptt
BATCH_SIZE = 32
EPOCH = 10
RESCHEDULED = False


# In[12]:


line_cache = texts.split('.')

corp = []
for unt in line_cache:
    unt = unt.strip('\n').lower()
    if len(unt) > 4:
        corp.append(unt.split())  

print(len(corp))
print(corp[0: 15])

# model1 = gensim.models.Word2Vec(corp, min_count=1, size=EMBED_SIZE, window=35, workers=4,
#                               alpha=0.001, seed=0, iter=35, sg=1)

model1 = gensim.models.Word2Vec(corp, min_count=1, size=EMBED_SIZE, window=35, workers=3,
                              alpha=0.001, seed=0, iter=25, sg=1)


# In[13]:


print('forest-creek', model1.similarity('forest','creek'))
# print('eat-drink', model1.similarity('hackers','cyber'))
# print('china-terrorist', model1.similarity('china','terrorist'))
# print('attack-cyber', model1.similarity('attack','cyber'))
# print('dog-cat', model1.similarity('dog','cat'))
# print('bird-flying', model1.similarity('bird','flying'))
# print('pig-flying', model1.similarity('pig','flying'))
# print('dog-news', model1.similarity('dog','news'))
# # print('terrorist-terror', model1.similarity('terrorist','terror'))
# print('he-she', model1.similarity('he','she'))
# print('he-his', model1.similarity('he','his'))
# # print('isis-terrorist', model1.similarity('isis','terrorist'))
# print('apple-top 5 concerned words', model1.most_similar('isis', topn=5))
# print('dog-top 5 concerned words', model1.most_similar('dog', topn=5))
# print(model1.doesnt_match('attack cyber dog defense fire hackers internet'.split()))
# print(model1.doesnt_match('run dog cat pig'.split()))
# print(model1.most_similar(positive=['cyber','attack'], negative=['country']))


# In[15]:


USE_CUDA = torch.cuda.is_available()
# gpus = [0]
# torch.cuda.set_device(gpus[0])

FloatTensor = torch.FloatTensor
LongTensor = torch.LongTensor
ByteTensor = torch.ByteTensor
flatten = lambda l: [item for sublist in l for item in sublist]


# In[16]:


def prepare_sequence(seq, to_index):
    idxs = list(map(lambda w: to_index[w] if to_index.get(w) is not None else to_index["<unk>"], seq))
    return LongTensor(idxs)


# In[17]:


def prepare_ptb_dataset(texts, word2index=None):
    corpus = [texts]
    corpus = flatten([co.strip().split() for co in corpus])

    if word2index == None:
        vocab = list(set(corpus))
        word2index = {'<unk>': 0}
        for vo in vocab:
            if word2index.get(vo) is None:
                word2index[vo] = len(word2index)
    
    return prepare_sequence(corpus, word2index), word2index


# In[18]:


def batchify(data, bsz):
    # Work out how cleanly we can divide the dataset into bsz parts.
    nbatch = data.size(0) // bsz
    # Trim off any extra elements that wouldn't cleanly fit (remainders).
    data = data.narrow(0, 0, nbatch * bsz)
    # Evenly divide the data across the bsz batches.
    data = data.view(bsz, -1).contiguous()
    if USE_CUDA:
        data = data.cuda()
    return data


# In[19]:


def getBatch(data, seq_length):
    size = data.size(1) - seq_length
    if size < 1:
        size = 1
    for i in range(0, size, seq_length):
        inputs = Variable(data[:, i: i + seq_length])
        targets = Variable(data[:, (i + 1): (i + 1) + seq_length].contiguous())
        yield (inputs, targets)


# In[20]:


train_data, word2index = prepare_ptb_dataset(texts)
index2word = {v:k for k, v in word2index.items()}

# save word2index
df_word2index = pd.DataFrame(columns=['keys', 'values'])
df_word2index['keys'] = list(word2index.keys())
df_word2index['values'] = list(word2index.values())
df_word2index = df_word2index.sort_values(by=['values'], ascending=1)
df_word2index.to_csv(path + 'word2index.csv', index=False)


# In[21]:


# pretrained_weight
wd_list = list(index2word.values())
pretrained_weight = []

for itm in wd_list:
    try:
        pretrained_weight.append(model1[itm])
    except Exception:
        pretrained_weight.append(np.random.random(EMBED_SIZE) * 2 - 1)
    
pretrained_weight = np.array(pretrained_weight)
print(pretrained_weight.shape)

# save pretrained_weight
df_pretrained_weight = pd.DataFrame(pretrained_weight)
df_pretrained_weight.to_csv(path + 'pretrained_weight.csv', index=False)
pretrained_weight


# In[22]:


class LanguageModel(nn.Module):
    def __init__(self, vocab_size, embedding_size, hidden_size, n_layers=1, 
                 pretrained_weight=pretrained_weight, dropout_p=0.25):

        super(LanguageModel, self).__init__()
        self.n_layers = n_layers
        self.hidden_size = hidden_size
        self.embed = nn.Embedding(vocab_size, embedding_size)
        self.rnn = nn.LSTM(embedding_size, hidden_size, n_layers, batch_first=True)
        self.linear = nn.Linear(hidden_size, vocab_size)
        self.dropout = nn.Dropout(dropout_p)
        
    def init_weight(self):
        self.embed.weight.data.copy_(torch.from_numpy(pretrained_weight))
        self.linear.weight = nn.init.xavier_uniform(self.linear.weight)
        self.linear.bias.data.fill_(0)
        
    def init_hidden(self,batch_size):
        hidden = Variable(torch.zeros(self.n_layers, batch_size, self.hidden_size))
        context = Variable(torch.zeros(self.n_layers, batch_size, self.hidden_size))
        return (hidden.cuda(), context.cuda()) if USE_CUDA else (hidden, context)
    
    def detach_hidden(self, hiddens):
        return tuple([hidden.detach() for hidden in hiddens])
    
    def forward(self, inputs, hidden, is_training=False): 
        embeds = self.embed(inputs)
        if is_training:
            embeds = self.dropout(embeds)
        out,hidden = self.rnn(embeds, hidden)
        return self.linear(out.contiguous().view(out.size(0) * out.size(1), -1)), hidden


# In[23]:


train_data = batchify(train_data, BATCH_SIZE)


# In[1]:


model = LanguageModel(len(word2index), EMBED_SIZE, HIDDEN_SIZE, NUM_LAYER, 0.3)
model.init_weight() 
if USE_CUDA:
    model = model.cuda()
loss_function = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=LR)


# In[25]:


for epoch in range(EPOCH):
    total_loss = 0
    losses = []
    hidden = model.init_hidden(BATCH_SIZE)
    for i,batch in enumerate(getBatch(train_data, SEQ_LENGTH)):
        inputs, targets = batch
        hidden = model.detach_hidden(hidden)
        model.zero_grad()
        preds, hidden = model(inputs, hidden, False)

        loss = loss_function(preds, targets.view(-1))
        losses.append(loss.data[0])
        loss.backward()
        torch.nn.utils.clip_grad_norm(model.parameters(), 0.5) # gradient clipping
        optimizer.step()
        
        if i > 0 and i % 500 == 0:
            print("[%02d/%d] mean_loss : %0.2f, Perplexity : %0.2f" % (epoch,EPOCH, np.mean(losses), np.exp(np.mean(losses))))
            losses = []
            
    # learning rate anealing
    if RESCHEDULED == False and epoch == EPOCH//2:
        LR *= 0.5
        optimizer = optim.Adam(model.parameters(), lr=LR)
        RESCHEDULED = True


# In[26]:


# prediction
sentences = ['Engineering giant GKN has rejected a ￡7.4bn hostile takeover bid from Melrose Industries. ', 
#                  'the army is determined to restore peace to the country.',
#              'the armies are determined to restore peace to the country.',
#              'the armies are determined of restore peace of the country.',
#              'pakistan has intensified its military campaign against extremist islamist groups.',
#              'russian government has attacked the base against huge amounts of islamic terrorists.',
#              'pakistan intensified its military campaigns against massive islamic groups last month.',
#              'north korean hackers have taken millions of dollars in virtual currencies.',
#              'north korean hackers have taken thousands of dollars in virtual currencies.',
#              'north korean hackers has gained millions of dollars in cyber world.',
#              'russian hackers attacked has eating of dollars in cyber world.',
#              'north korean government has launched a missile successfully last month.',
#              'north korean government has launched a missile successful last month.',
#              'north korean government have launched a missile successfully last month.',
#              'north korean hackers haven eaten a lot of green vegetables.',
#              'north korean hackers have a lot of eaten green vegetables',
#              'north korean pigs have taken millions of dollars in virtual currencies.',
#              'the beautiful girl is dressed in a red shirt.',
#              'the beautiful boy is dressed in a red shirt.',
#              'the beautifulgirl is dressed in a red computer.',
#              'there is a pig flying in the blue sky.',
#              'there is a bird flying in the blue sky.',
#              'there are a tiger flying in the blue sky.',
#              'we simply have to get out and do it if we can make a difference through our involvement.',
#              'we simply have to get out and do it if we can make a difference through the apple.',
#              'we simply have to out get and do it if we can make a difference through the apple.',
#              'they might have some bleeding at the time of birth and that blood can also plug up these channels.',
#              'they have might some bleeding at the year of birth and that blood can also plastic up these channels.', 
#              'they might have some bleeding at the time of blood and that blood can also plug up these tunnles.',
#              'the red apple tastes really sweet.',
#              'the red pear smells really sweet.',
#              'the red chair tastes really sweet.',
#              'he thinks it reflects mainly that the focus of the meetings was to keep the meetings alive.',
#              'i thinks it reflect mainly that the focus of the negotiations was to keep the negotiations alive.',
#              'i thought it reflects mainly that the focus of the negotiations is to keeps the negotiations alive.',
#              'russian government has to take actions to deal with massive terror attacks.',
#              'russian government wants to take actions to deal with massive terror attacks.',
#              'russian government decides to take actions to deal with massive terror attacks.',
#              'u.s. government has finally made its decision to deal with cyber attacks.', 
#              'russian governnment has to take actions to deal with massive terror attacks.',
#              'russian government have to taking actions to deal with massive terror attacks.',
#              'russian government has to actions made to deal with massive terror attacks.',
#              'u.s. government has to dealing with massive attacks terror in recent years.'
            ]
print('sentences number:', len(sentences))

sentences_clean = []
for itm in sentences:
    itm = clean(itm, re_first)
    itm = clean(itm, re_dict)
    itm = clean(itm, re_symb)
    itm = clean(itm, re_dict)
    itm = clean(itm, re_number)
    sentences_clean.append(itm)
    
sentences_proc = []
for itm in sentences_clean:
    no = len(itm.split())
    itm = itm + ' ' + '. ' * (SEQ_LENGTH - no - 1) + '.'
    sentences_proc.append(itm.strip())

position = []
for itm in sentences_proc:
    position.append(itm.split().index('.') - 1)


# In[27]:


for k, itm in enumerate(sentences_proc):
    print(itm.replace('.', ''))
    
    test_data, _ = prepare_ptb_dataset(itm, word2index)
    test_data = batchify(test_data, BATCH_SIZE//BATCH_SIZE)

    total_loss = 0
    hidden = model.init_hidden(BATCH_SIZE//BATCH_SIZE)
    for i, batch in enumerate(getBatch(test_data, SEQ_LENGTH)):
        inputs, targets = batch
        hidden = model.detach_hidden(hidden)
        model.zero_grad()
        preds, hidden = model(inputs, hidden)

        continue_prob = 0
        for i in range(SEQ_LENGTH):
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

