# -*- coding:utf-8 -*-
import logging
import re

import gensim
from gensim.models import word2vec

from PreProcessing.DataCleanEngineMp import DataCleanEngineMp

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


class PrepareWordVector(DataCleanEngineMp):
    def __init__(self):
        super(PrepareWordVector, self).__init__()
        # configuration for the gensim to train the word vector
        self.EMBED_SIZE = 128

    def recursive_find_all_text(self, lst_in_depth):
        if not isinstance(lst_in_depth[0], str):
            for lists in lst_in_depth:
                lst_in_depth[0].extend(lists)
            return self.recursive_find_all_text(lst_in_depth[0])
        else:
            text_string = " ".join(lst_in_depth)
            # handle the empty string, due to them made the empty block
            re.sub(" +", " ", text_string)
            return text_string

    # test passed 2018/12/29, good to go
    def get_the_model_with_gensim(self):
        instance_to_use = DataCleanEngineMp()
        texts_unknow_depth = instance_to_use.mp_based_the_clean_engine_core()

        # process the unknown
        texts = self.recursive_find_all_text(texts_unknow_depth)
        print("this is the text:", texts)
        # the processed texts
        line_cache = texts.split('.')
        corp = []
        for unt in line_cache:
            unt = unt.strip('\n').lower()
            if len(unt) > 4:
                corp.append(unt.split())

        print(len(corp))
        print(corp[0: 15])
        # A testing model, parameters modified
        # model1 = gensim.models.Word2Vec(corp, min_count=1, size=EMBED_SIZE, window=35, workers=4,
        #                               alpha=0.001, seed=0, iter=35, sg=1)
        model_to_use = gensim.models.Word2Vec(
            corp, min_count=1, size=self.EMBED_SIZE, window=35, workers=3,
            alpha=0.001, seed=0, iter=25, sg=1
        )

        return model_to_use
