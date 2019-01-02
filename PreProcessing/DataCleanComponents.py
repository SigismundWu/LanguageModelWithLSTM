# -*- coding: utf-8 -*-
import os
import re
import time

from PreProcessing.RegexPattern import RegexPattern


class DataCleanComponents(object):
    """Data clean of the nlp data for the Language Model"""
    def __init__(self):
        # init the regex pattern class, get regex pattern and rules for pre processing
        self.regex_patterns = RegexPattern
        self.search_path = '../Data/gutenburg/'

    @classmethod
    def pre_data_clean(cls, texts, re_lists, final=False) -> str:
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

    # fast enough, single process with single Thread is good
    def get_the_training_data(self) -> list:
        file_name = []
        for parent, subfolders, files in os.walk(self.search_path):
            for i, unt in enumerate(files):
                unt = os.path.join(parent, unt)
                # if DS_store in the str, then -1, then deprecate this path
                if (unt.find('DS_Store') < 0) & (os.path.getsize(unt) > 0):
                    file_name.append(unt)

        return file_name

    @classmethod
    def divide_into_2(cls, lst) -> tuple:
        """slice the divide more smoothly"""
        list_full_length = len(lst)
        list_first_part = lst[:list_full_length // 2]
        list_rest_part = lst[list_full_length // 2:]
        return list_first_part, list_rest_part

    def divide_the_lst_into_4(self, lst) -> list:
        """divide the list into four parts as average as possible, so divide into 2 for twice, as fast as it can"""
        # the first time
        first_time_outcome = self.divide_into_2(lst)
        # the second time, map it
        second_time_outcome = list(map(list, map(self.divide_into_2, self.divide_into_2(first_time_outcome))))
        # concatenate and finish it into a nesting list like [[str, str...], [str, str...], ...]
        [second_time_outcome[0].extend(lists) for lists in second_time_outcome[1:]]
        final_task_distribute_list = second_time_outcome[0]

        return final_task_distribute_list

    def divide_the_lst_into_counts(self, lst, counts):
        """
        divide them into a number that decided by the cpu cores
        if the counts even bigger than the all_length, then divide then into one each sub list
        """
        final_task_list = list()
        start_low_bound = 0
        all_length = len(lst)
        if counts > all_length:
            counts = all_length

        each_bound_length = all_length // counts
        while counts > 1:
            final_task_list.append(lst[start_low_bound:start_low_bound + each_bound_length])
            start_low_bound += each_bound_length
            counts -= 1

        final_task_list.append(lst[start_low_bound:])
        # smooth the last parameter with divide_into_2, and you always get a list one more than your cpu counts
        post_process = self.divide_into_2(final_task_list[-1])
        processed_finall_list = final_task_list[:-1]
        processed_finall_list.append(post_process[0])
        processed_finall_list.append(post_process[1])

        return processed_finall_list

    def clean_data_with_re_patterns(self, texts):
        # get from the regex setting class
        pattern = re.compile('.{10}\d+.{10}', re.I)
        res = re.findall(pattern, texts)
        print('dirty data before cleaning:', len(res))

        # data cleaning
        texts = self.pre_data_clean(texts, self.regex_patterns.re_first)
        print('re_first_finished')
        texts = self.pre_data_clean(texts, self.regex_patterns.re_dict)
        print('re_dict_finished')
        texts = self.pre_data_clean(texts, self.regex_patterns.re_symb)
        print('re_symb_finished')
        texts = self.pre_data_clean(texts, self.regex_patterns.re_dict)
        # print('re_dict_finished')
        texts = self.pre_data_clean(texts, self.regex_patterns.re_number, final=True)
        print('re_number_finished')

        texts = texts.lower().strip()
        print(texts[1000: 2000])

        # dirty data size after cleaning
        pattern = re.compile('.{50}\d+.{50}', re.I)
        res = re.findall(pattern, texts)
        print('dirty data after cleaning:', len(res))

        return res
