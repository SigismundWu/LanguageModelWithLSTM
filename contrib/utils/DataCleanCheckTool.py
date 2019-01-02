# -*- coding: utf-8 -*-
import re


class DataCleanCheckTool(object):
    """General tool to check whether the text have such issues"""

    @classmethod
    def cc_chinese(cls, check_str):
        check_list = []

        for ch in check_str:
            if u'\u4e00' <= ch <= u'\u9fff':
                check_list.append(True)
            else:
                check_list.append(False)

        if any(check_list):
            return True
        else:
            return False

    @classmethod
    def cc_alphabet(cls, check_str):
        check_list = []

        for uchar in check_str:
            if (u'\u0041' <= uchar <= u'\u005a') or (u'\u0061' <= uchar <= u'\u007a'):
                check_list.append(True)
            else:
                check_list.append(False)

        if any(check_list):
            return True
        else:
            return False

    @classmethod
    def cc_number(cls, check_str):
        for uchar in check_str:
            if u'\u0030' <= uchar <= u'\u0039':
                return True
            else:
                return False

    @classmethod
    def select_u_s_qt(cls, dict):
        index_list = []

        for k, v in dict.items():
            if "." in v:
                index_list.append(k)
            elif "!" in v:
                index_list.append(k)
            elif "?" in v:
                index_list.append(k)
            else:
                pass

        return index_list

    @classmethod
    def check_sents(cls, check_str):
        check_list = []
        punc_list = [',', '.', ':', ';', '?', '(', ')', '!', '*', '@', '# ', '$', '%', '’', ' ']  # 别忘了空格

        for uchar in check_str:
            if (u'\u0041' <= uchar <= u'\u005a') or (u'\u0061' <= uchar <= u'\u007a'):
                check_list.append(True)
            elif u'\u0030' <= uchar <= u'\u0039':
                check_list.append(True)
            elif uchar in punc_list:
                check_list.append(True)
            else:
                check_list.append(False)

        if all(check_list):
            return True
        else:
            return False

    @classmethod
    def c_chinese_punc(cls, list):

        for key, str in enumerate(list):
            if "！" in str:
                list[key] = re.sub("！", "!", list[key])
            elif "，" in str:
                list[key] = re.sub("，", ",", list[key])
            elif "。" in str:
                list[key] = re.sub("。", ".", list[key])
            elif "’" in str:
                list[key] = re.sub("’", "'", list[key])
            else:
                pass

        return list

    @classmethod
    def check_sw(cls, string):
        try:
            re.match("^[A-Z]", string).group()
            return string
        except:
            pass

    @classmethod
    def delete_chinese(cls, check_str):
        for ch in check_str:
            if u'\u4e00' <= ch <= u'\u9fff':
                check_str = check_str.replace(ch, "")
            else:
                pass
        return check_str

    @classmethod
    def is_chinese(cls, ch):
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
        else:
            return False

    def check_s_replace(self, string):
        new_string = ""

        pattern_dquo_marks = re.compile('“|”')
        string = pattern_dquo_marks.sub('"', string)
        pattern_squo_marks = re.compile("‘|’")
        string = pattern_squo_marks.sub("'", string)

        for i in range(len(string)):

            if i < len(string) - 1:
                #         try:
                if (string[i] == "'") | (string[i] == '"'):
                    if self.is_chinese(string[i + 1]) | self.is_chinese(string[i - 1]):
                        pass
                    else:  # 这个else append的是不包裹中文的引号
                        new_string += string[i]
                else:
                    new_string += string[i]  # 这个else append的是除了进入上一个判断的所有字符串
            else:
                if (string[i] == "'") | (string[i] == '"'):
                    if self.is_chinese(string[i - 1]):
                        pass
                    else:  # 这个else append的是不包裹中文的引号
                        new_string += string[i]
                else:
                    new_string += string[i]  # 这个else append的是除了进入上一个判断的所有字符串
        return new_string

    @classmethod
    def check_swu(cls, string):
        try:
            re.match("^[A-Z]", string).group()
            return True
        except Exception as e:
            return False

    @classmethod
    def check_swl(cls, string):
        try:
            re.match("^[a-z]", string).group()
            return True
        except Exception as e:
            return False

    @classmethod
    def check_ewep(cls, string):
        endpunc = [".", "!", "?", '"']  # 这个双引号也是特殊情况，需要被考虑的，这个暂时这样处理，目前所能发现的双引号结尾的都结束的

        if string[-1] in endpunc:
            return True
        else:
            return False
