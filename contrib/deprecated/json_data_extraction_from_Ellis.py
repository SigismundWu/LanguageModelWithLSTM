import logging
import json

import pandas as pd

data_tmjcxx = pd.read_csv("tmjcxx.csv")

json_list = list(data_tmjcxx["json_text"])
json_dict_list = []

for i in json_list:
    try:
        json_dict_list.append(json.loads(i))
    except Exception as e:
        logging.exception(e)


def generate_df(json_dict_list):
    list_for_dataframe = []
    each_item_list = []
    
    for item in json_dict_list:
        # 通过选项作为最大数量的项
        for index in range(len(item["data"])):
            try:
                if item["data"][index]["components"] is []:

                        each_item_list.append(item["code"])
                        # 这一列是option_id
                        each_item_list.append("")
                        # 这一列是是否为key
                        each_item_list.append("")
                        # 这一列是text
                        each_item_list.append("")
                        # 这一列是question_text
                        each_item_list.append(item["data"][index]["question"]["text"])
                        # 这一列是question_id
                        each_item_list.append(item["data"][index]["id"])
                        # 中文name
                        each_item_list.append(item["name"].split(" ")[-1])
                        # 这一列是module_id
                        each_item_list.append(item["params"]["module"])

                        list_for_dataframe.append(each_item_list)
                        each_item_list = []

                else:
                    try:
                        # 这一列是exercise_id
                        each_item_list.append(item["code"])
                        # 这一列是option_id
                        each_item_list.append(item["data"][index]["components"][0]["id"])
                        # 这一列是是否为key
                        each_item_list.append(item["data"][index]["components"][0]["is_key"])
                        # 这一列是text
                        each_item_list.append(item["data"][index]["components"][0]["text"])
                        # 这一列是question_text
                        each_item_list.append(item["data"][index]["question"]["text"])
                        # 这一列是question_id
                        each_item_list.append(item["data"][index]["id"])
                        # 中文name
                        each_item_list.append(item["name"].split(" ")[-1])
                        # 这一列是module_id
                        each_item_list.append(item["params"]["module"])

                        list_for_dataframe.append(each_item_list)
                        each_item_list = []

                    except Exception as e:
                        logging.exception(e)
            except Exception as e:
                logging.exception(e)
    dataframe = pd.DataFrame(list_for_dataframe, columns=["exercise_id","option_id","is_key",
                                                            "text", "question_text",
                                                            "question_id",
                                                            "Chinese_name","module_id"])
    
    return dataframe


# 一些属于哪本书哪一册的基础信息等
data_jcxx = pd.read_csv("./tmjcxx.csv")
data_jcxx.drop(axis = 1, columns = "json_text", inplace = True)
data_tmp = data_jcxx[["course_id", "course_ename", "course_unit_id", "unit_name", "exercise_id", "template_id", "parameter"]]

df = generate_df(json_dict_list)
df_final = pd.merge(df, data_tmp, on = "exercise_id" ,how = "left")
df_final.to_csv("data_from_Ellis_json_final.csv", encoding = "utf-8")
