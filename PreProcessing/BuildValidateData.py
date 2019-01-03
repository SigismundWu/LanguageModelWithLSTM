# -*- coding:utf-8 -*-
import re


class BuildValidateData(object):
    def __init__(self):
        self.path = "../Data/ALO7/alo7qtp.txt"

    def read_data(self):
        print("building validate data")
        with open(self.path, "r",encoding="utf-8") as data_file:
            data = data_file.readlines()
        # finish the process of validate data
        data = list(map(lambda x: re.sub("\n", "", x), data))
        print("validate data built")

        return data
