# -*- coding:utf-8 -*-
import logging
import re

import pandas as pd

from contrib.utils.DataCleanCheckTool import DataCleanCheckTool


class CorpusFromEllisQTWB(object):
    """
    CorpusFromEllis, question_text without blank
    由于存在大量单个单词和没有空格句子各种没有意义的a;an这类的语句或者答案，因此需要划分
    """
    def __init__(self):
        # the [0] is data_qt, [1] is data_qt_d
        self.set_of_result = self.get_processed_data()
        self.all_sents = self.process_special_sign()
        # build the a_s_index which is used to do the comparison
        self.a_s_index = self.build_the_index()
        # get processed check_list_0
        self.check_list_0 = self.semi_final_process()

    @classmethod
    def get_processed_data(cls):
        # 读进之前merge好并导出成csv的dataset
        data = pd.read_csv("data_ready_to_use.csv", index_col=0)
        # 列表中有exercise_id和这个是否是published的exercise，目前只用published的版本，提高corpus的质量
        # 两种类型的可以被使用，一个是published，一个是verified
        data_fillter = pd.read_csv("exercise_status.csv", index_col=0)
        data_fillter.reset_index(inplace=True)
        data_fillter.rename({"ExerciseID": "exercise_id"}, inplace=True, axis=1)
        # 完整的data完成之后应该是这样的
        data_ff = pd.merge(data, data_fillter, on="exercise_id", how="left")
        # 然后只保留有verified和published的部分
        # 后续的部分全部都在data_ff上，代替掉之前那个data
        # 然后由于只采用了published和verified的版本，因此语料总数减少了
        data_ff = data_ff[(data_ff.Status == "verified") | (data_ff.Status == "published")]

        data_qt = data_ff.dropna(subset=["question_text"])
        data_qt.reset_index(inplace=True, drop=True)
        # 首先是找出是句子的那些question_text

        data_qt_d = data_qt.to_dict()
        index_list = DataCleanCheckTool.select_u_s_qt(data_qt_d["question_text"])
        data_qt = data_qt.iloc[index_list]
        data_qt.reset_index(inplace=True, drop=True)
        data_qt = data_qt[data_qt.is_key is True]
        data_qt.reset_index(inplace=True, drop=True)
        data_qt.drop_duplicates(subset=["exercise_id", "question_text"], inplace=True)
        data_qt.reset_index(inplace=True, drop=True)
        data_qt_d = data_qt.to_dict()

        return data_qt, data_qt_d

    def process_special_sign(self):
        """filter of the special sign"""
        # 首先把全部是英文的句子找出来，没有特殊符号，没有其他东西，只有字母和数字。
        # 思路大概是用正则表达式确定结尾，用函数判断中间全部都是英文的句子，不允许特殊符号。
        # 用上面的check_sents函数，解决这个问题。
        all_sents = list()
        for i in self.set_of_result[0]["question_text"]:
            if DataCleanCheckTool.check_sents(i):
                all_sents.append(i)

        # 有些特殊情况的数据，直接抛弃掉，数量不大
        # 然后有一些描述词性特殊的单词的其实没有意义，直接抛掉
        # 还有一些带括号的，那些需要把括号中的内容抛掉
        # 但是因为用的是pop，每次pop之后index都变化，所以会跳着pop，因此在数据量大的情况下需要重复执行
        for k, v in enumerate(all_sents):
            if ". . ." in v:
                all_sents.pop(k)
            elif "..." in v:
                all_sents.pop(k)
            elif "adj." in v:
                all_sents.pop(k)
            elif "adv." in v:
                all_sents.pop(k)
            elif "n." in v:
                all_sents.pop(k)
            elif "v." in v:
                all_sents.pop(k)
            elif "prep." in v:
                all_sents.pop(k)
            elif "sth." in v:
                all_sents.pop(k)
            elif "sb." in v:
                all_sents.pop(k)

        # 小写开头的都可以全部抛弃掉了，不是完整的真正的句子，只是一段不完整的话。
        pattern = re.compile("^[a-z].+")
        for k, v in enumerate(all_sents):
            try:
                pattern.search(v).group()
                all_sents.pop(k)
            except Exception as e:
                logging.exception(e)

        return all_sents

    def build_the_index(self):
        a_s_index = list()
        for k, v in self.set_of_result[1]["question_text"].items():
            if v in self.all_sents:
                a_s_index.append(k)
            else:
                pass

        return a_s_index

    def semi_final_process(self):
        self.set_of_result[0].reset_index(inplace=True, drop=True)
        data_all_s = self.set_of_result[0].iloc[self.a_s_index]
        data_all_s.drop_duplicates(subset=["exercise_id", "question_text"], inplace=True)
        data_all_s.reset_index(inplace=True, drop=True)
        data_all_s = data_all_s.astype(str)

        check_list_0 = []
        for i in range(len(data_all_s)):
            check_list_0.append(
                data_all_s.iloc[i]["question_text"] +
                "{platform:" + "Ellis" + "}" +
                "{type:" + "question_text" + "}" +
                "{is_key:" + data_all_s.iloc[i]["is_key"] + "}" 
                "{exercise_id:" + data_all_s.iloc[i]["exercise_id"] + "}" +
                "{course_id:" + data_all_s.iloc[i]["course_id"] + "}" +
                "{unit:" + data_all_s.iloc[i]["course_unit_id"] + "}" +
                "{parameter:" + data_all_s.iloc[i]["parameter"] + "}" +
                "{question_id:" + data_all_s.iloc[i]["question_id"] + "}" +
                "{package_id:" + data_all_s.iloc[i]["package_id"] + "}" +
                "{Status:" + data_all_s.iloc[i]["Status"] + "}" +
                "{isfilled:No}"
            )

        # 加上|n
        for i in range(len(check_list_0)):
            check_list_0[i] = check_list_0[i] + "\n"

        return check_list_0

    def final_process(self):
        # 这一步最后再做，不然读取数据的时候会有问题
        # 就在全部读进列表之后处理吧
        # 去掉那些不要的括号中的内容，这些是改写句子，其实在text部分中都已经有，去掉也不影响本身句子的完整性
        # 为了能方便处理这其中的小括号，中括号等，需要考虑一个装各种参数的方式
        # 看了一下就决定是{}了，大括号只有一个，还是没什么用的
        pattern = re.compile("\(.+\)")
        for i in range(len(self.check_list_0)):
            try:
                self.check_list_0[i] = pattern.sub("", self.check_list_0[i])
            except Exception as e:
                logging.exception(e)

        # 去掉开头的数字
        pattern = re.compile("^\d+\.")
        for i in range(len(self.check_list_0)):
            try:
                self.check_list_0[i] = pattern.sub("", self.check_list_0[i])
            except Exception as e:
                logging.exception(e)

        pattern = re.compile("’")
        for i in range(len(self.check_list_0)):
            try:
                self.check_list_0[i] = pattern.sub("'", self.check_list_0[i])
            except Exception as e:
                logging.exception(e)

        with open("corpus from Ellis(question_text without blank).txt", "w", encoding = "utf-8") as f:
            f.writelines(self.check_list_0)

        return
