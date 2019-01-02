# -*- coding:utf-8 -*-
import logging
import re

import pandas as pd

from contrib.utils.DataCleanCheckTool import DataCleanCheckTool


class CorpusFromEllisText(object):
    """The class to process the Text in Ellis to establish the corpus for text"""
    def __init__(self):
        self.data_ff = self.prepare_the_data()
        self.data = pd.read_csv("data_ready_to_use.csv", index_col = 0)

    @classmethod
    def prepare_the_data(cls):
        data_ep = pd.read_csv("exercise_package.csv")
        data = pd.read_csv("full_without_json.csv", index_col = 0)
        data = pd.merge(data, data_ep, on = "exercise_id", how = "left")
        data.drop(["id", "course_chinesename", "course_ename", "template_id", "unit_name"], axis = 1, inplace = True)
        data.to_csv("data_ready_to_use.csv")
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

        return data_ff

    def select_useful_info(self):
        # warning：在text中存在大量的中文符号的问题，要进行替换，这个需要注意
        # 典型的就是it's的上撇号，例如说it’s,此外还有中文句号，中文感叹号，中文问号等等
        # 为了方便使用，各种类型的都做成index的list，这样只是在生成index的时候稍微慢点，但是一旦有了index会比较方便
        # 首先text中所有NA去掉
        data_text = self.data_ff.dropna(subset=["text"])
        data_text.reset_index(inplace=True, drop=True)
        # 首先去掉所有只有一个词的，即选择题，所有的A,B,T,F之类的，<=2是因为还有很多挖空填词，也是这个长度
        # drop掉这些之后，其中一些两个词的中文词汇词汇被drop掉，后面也少了一些中文判断中的麻烦
        # 另外像hi这类停止词一类的，也会被直接drop掉，没有什么意义
        d_schar_list = []
        for index in range(len(data_text["text"])):
            if len(data_text["text"][index]) <= 2:
                d_schar_list.append(index)

        data_text.drop(d_schar_list, inplace=True)
        data_text.reset_index(inplace=True, drop=True)
        # 拼写测试的有问题，因为存在乱序的问题，所以拼写测试的部分会等一下单独处理，首先处理掉没有拼写测试的
        # 除此之外，找不同题型和其他带斜杠要划分的，也要单独处理
        # 接下来先去掉大量的无法使用的中文
        d_chinese_list = []
        for i in range(len(data_text["text"])):
            if DataCleanCheckTool.cc_chinese(data_text.iloc[i]["text"]):
                d_chinese_list.append(i)

        data_text.drop(d_chinese_list, inplace=True)
        data_text.reset_index(inplace=True, drop=True)
        # 拼写测试和文字连线两个类型的题目是真的完全无价值的
        data_without_px_wz = data_text[(data_text.name != "拼写测试") & (data_text.name != "文字连线")]
        data_without_px_wz.reset_index(inplace=True, drop=True)
        # deprecated, only reserved for accident
        # 有点慢，但是知道index的好处很大，所以又不能放弃取index，这个比较纠结，应该有更好的方法
        # d_u_list = []
        # for index in range(len(data_without_px_wz["text"])):
        #     if (("/" in data_without_px_wz.iloc[index]["text"]) |
        #         ("|" in data_without_px_wz.iloc[index]["text"]) |
        #         (";" in data_without_px_wz.iloc[index]["text"])):
        #         d_u_list.append(index)
        # And we present a new_version down here
        data_d = data_without_px_wz.to_dict()
        e_l = []
        for k,v in data_d["text"].items():
            if "|" in v:
                e_l.append(k)
            elif "/" in v:
                e_l.append(k)
            elif ";" in v:
                e_l.append(k)
            else:
                pass

        data_with_break = data_without_px_wz.iloc[e_l]
        data_with_break.reset_index(inplace = True, drop = True)
        # 鉴于文字连线和拼写测试在我们的语料库建设中确实不会有任何价值意义，因为在这里更新data_text
        data_text = data_without_px_wz.drop(e_l)
        data_text.reset_index(inplace=True, drop=True)
        # 这一步之后，data_text已经是去掉了那些带break的和少了那两种没有意义的题型的了
        # 下面的逻辑是：因为阅读理解分区里面存在大量学生其实只看过一次的文本，所以应该用下面的两个drop_duplicates
        data_text.drop_duplicates(subset=["text", "exercise_id"], inplace=True)
        data_with_break.drop_duplicates(subset=["text", "exercise_id"], inplace=True)
        data_text.reset_index(inplace=True, drop=True)
        data_with_break.reset_index(inplace=True, drop=True)
        # deprecated
        # data_text["is_key"].replace({True:"1", False:"0"}, inplace = True)
        # data_with_break["is_key"].replace({True:"1", False:"0"}, inplace = True)
        # data_with_break["is_key"].replace({"1":"1", "0":"2"}, inplace = True)
        data_with_break = data_with_break.astype(str)

        return data_text, data_with_break

    def tag_the_text(self, data_with_break):
        # 这里有两个循环，这两个循环是为了提取出全部是句子的index，用dataframe操作
        # 加上最后的部分是处理data_with_break中还存在的那部分句子数据
        # 但是这个明显还不是完整版的，最后的check_list那里还要增加更多的变量列
        sents_l = []
        for i in data_with_break["text"]:
            if "." in i:
                sents_l.append(i)
            elif "?" in i:
                sents_l.append(i)
            elif "!" in i:
                sents_l.append(i)

        sents_l2 = []
        for i in sents_l:
            if "|" in i:
                sents_l2.append(i)
            else:
                pass
        # 下面是为语料库里的内容打上标签
        check_list = []
        for item in sents_l2:
            check_list.append(
                item + "(platform:" + "Ellis" + ")" +
                "(type:" + "text" + ")" +
                "(is_key:" + data_with_break[data_with_break["text"] == i]["is_key"] + ")" 
                "(exercise_id:" + data_with_break[data_with_break["text"] == i]["exercise_id"] + ")" +
                "(course_id:" + data_with_break[data_with_break["text"] == i]["course_id"] + ")" +
                "(unit:" + data_with_break[data_with_break["text"] == i]["course_unit_id"] + ")" +
                "(parameter:" + data_with_break[data_with_break["text"] == i]["parameter"] + ")" +
                "(question_id:" + data_with_break[data_with_break["text"] == i]["question_id"] + ")" +
                "(package_id:" + data_with_break[data_with_break["text"] == i]["package_id"] + ")" +
                "(Status:" + data_with_break[data_with_break["text"] == i]["Status"] + ")"
            )
        # 因为上面产生的是一个包含了pd.series的列表，所以下面需要再用循环处理这个列表，提取出所有东西
        # 因此这是一个final_list，这个final_list里面包含的内容就是
        final_list = []
        for i in check_list:
            for j in list(i):
                final_list.append(j)
        # 这个或的符号必须要转义，不转义正则无法判断，因此通过这个正则表达式，顺利处理掉了中间的空
        pattern = re.compile("\|")
        for i in range(len(final_list)):
            final_list[i] = pattern.sub(" ",final_list[i])
        # 这里之所以要用空格不用""这样的空字符串是因为有些字符是跟|黏在一起的，用空格才不会产生黏在一起的问题，但是其他有空格的就会产生问题
        # 因此下面再添加一个循环进行检测，把这些双空格号替换回一个空格号
        pattern0 = re.compile("  ")
        for i in range(len(final_list)):
            final_list[i] = pattern0.sub(" ", final_list[i])
        # 为所有字符添加上换行符，写入txt
        for i in range(len(final_list)):
            final_list[i] = final_list[i] + "\n"
        # final_list其实一共有两个部分，这个只是处理了withbreak的部分，这里重赋值，把这个让出来
        final_list_with_break = final_list

        return final_list_with_break

        # deprecated method, as doc string, to keep record, might deleted in future
        # 下面这个方法太慢，已经被被抛弃，因为组合后面的输出太慢了这个方法
        # 一般text中有用的部分就是这些，其他的恐怕没有什么意义了
        # data_text_rd = data_text[(data_text["name"] != "翻译选择")&
        #                          (data_text["name"] != "连词成句")&
        #                          (data["name"] != "单项选择加长234")]
        # index_rd_list = []
        # sents_l = []
        # for i in data_text_rd["text"]:
        #     if "." in i:
        #         sents_l.append(i)
        #     elif "?" in i:
        #         sents_l.append(i)
        #     elif "!" in i:
        #         sents_l.append(i)
        # # 这几个题型只有是True的才有意义，所以把他们放到一起
        # data_text_st = data_text[(data_text["name"] == "翻译选择")|
        #                          (data_text["name"] == "连词成句")|
        #                          (data["name"] == "单项选择加长234")]
        # data_text_st = data_text_st[data_text_st.is_key == True]
        # # 把那三个只能是True的题型补充进去
        # for i in data_text_st["text"]:
        #     if "." in i:
        #         sents_l.append(i)
        #     elif "?" in i:
        #         sents_l.append(i)
        #     elif "!" in i:
        #         sents_l.append(i)
        # #两个表concat起来，然后这样的话下面的处理只需要一次，减少成本，等一下还要再处理
        # data_text_final = pd.concat([data_text_rd, data_text_st],axis = 0)

    def process_data_text(self, data_text):
        # 是的，这个改进过的调用字符串的方法，超级快
        data_text_rd = data_text[(data_text["name"] != "翻译选择")&
                                 (data_text["name"] != "连词成句")&
                                 (self.data["name"] != "单项选择加长234")]

        data_rd_d = data_text_rd.to_dict()

        index_list = []
        for k,v in data_rd_d["text"].items():
            if "." in v:
                index_list.append(k)
            elif "?" in v:
                index_list.append(k)
            elif "!" in v:
                index_list.append(k)

        data_text_st = data_text[(data_text["name"] == "翻译选择")|
                                 (data_text["name"] == "连词成句")|
                                 (self.data["name"] == "单项选择加长234")]
        # 选择全是True的，然后
        data_text_st = data_text_st[data_text_st.is_key is True]
        data_st_d = data_text_st.to_dict()
        # 把那三个只能是True的题型补充进去
        for k,v in data_st_d["text"].items():
            if "." in v:
                index_list.append(k)
            elif "?" in v:
                index_list.append(k)
            elif "!" in v:
                index_list.append(k)

        data_text_final = data_text.iloc[index_list]
        data_text_final.reset_index(inplace=True, drop=True)
        data_text_final = data_text_final.astype(str)

        return data_text_final

    def post_process(self, data_text_final, final_list_withbreak):
        # 这个写好之后，整个dataframe转成str，就没那么多问题了，可以直接导出了
        check_list_0 = []
        for i in range(len(data_text_final)):
            check_list_0.append(
                data_text_final.iloc[i]["text"] +
                "(platform:" + "Ellis" + ")" +
                "(type:" + "text" + ")" +
                "(is_key:" + data_text_final.iloc[i]["is_key"] + ")" 
                "(exercise_id:" + data_text_final.iloc[i]["exercise_id"] + ")" +
                "(course_id:" + data_text_final.iloc[i]["course_id"] + ")" +
                "(unit:" + data_text_final.iloc[i]["course_unit_id"] + ")" +
                "(parameter:" + data_text_final.iloc[i]["parameter"] + ")" +
                "(question_id:" + data_text_final.iloc[i]["question_id"] + ")" +
                "(package_id:" + data_text_final.iloc[i]["package_id"] + ")" +
                "(Status:" + data_text_final.iloc[i]["Status"] + ")"
            )
            # 加上|n
            for i in range(len(check_list_0)):
                check_list_0[i] = check_list_0[i] + "\n"
            """
            some deprecated codes and its explanation, see down below
            关于这些题型本身，有太多的内容没有意义用不上了
            px的text里面全部都是单词，没有意义，所以不要了
            data_text_px = data_text[data_text.name == "拼写测试"]
            wz里面主要都是单词，而且还是不完整单词，也基本上可以不用了
            data_text_wz = data_text[data_text.name == "文字连线"]
            全部都是单词，干脆不要
            data_text_kt = data_text[data_text.name == "T看图拼写"]
            全部是单词
            data_text_dc = data_text[data_text.name == "T单词拼写"]
            这个还是有价值的
            data_text_dx = data_text[data_text.name == "单项选择加长234"]
            翻译，这里面有不少句子
            data_text_fy = data_text[data_text.name == "翻译选择"]
            data_text_fy = data_text_fy[data_text_fy.is_key == True]
            连词也是，但还必须是正确答案
            data_text_lc = data_text[data_text.name == "连词成句"]
            data_text_lc = data_text_lc[data_text_lc.is_key == True]
            data_text_dx = data_text_dx[data_text_dx.is_key == True]
            data_text_dx.drop_duplicates(subset=["text", "exercise_id"], inplace = True)
            """
            # 去掉prefix的序号
            def d_prefix_num(iterable):
                # 一些题目标号需要被去掉
                pattern = re.compile("^\d{1}\.")
                for i in range(len(iterable)):
                    try:
                        iterable[i] = pattern.sub("", iterable[i])
                    except Exception as e:
                        logging.exception(e)

            # 首先去掉有prefix的，这些序号都没有意义
            d_prefix_num(check_list_0)
            d_prefix_num(final_list_withbreak)

            # 然后替换那些中文符号，目前发现存在的是"’"和"，"
            # 这些中文符号已经全部处理掉了
            def c_chinese_punc(list):
                for key, str in enumerate(list):
                    if "！" in str:
                        list[key] = re.sub("！","!",list[key])
                    elif "，" in str:
                        list[key] = re.sub("，",",",list[key])
                    elif "。" in str:
                        list[key] = re.sub("。",".",list[key])
                    elif "’" in str:
                        list[key] = re.sub("’","'",list[key])
                    else:
                        pass

            # 中文符号被处理掉了
            c_chinese_punc(check_list_0)
            c_chinese_punc(final_list_withbreak)
            """
            def pop0(list):
                for key,string in enumerate(list):
                    if "..." in string:
                        list.pop(key)
                    elif ". . ." in string:
                        list.pop(key)
                    else:
                        pass
            """
        # 前面都处理完后在这里统一写入
        with open("corpus from Ellis(text).txt", "w", encoding="utf-8") as f0:
            f0.writelines(check_list_0)
