# -*-coding:UTF-8 -*-
'''
* data_utils.py
* @author wuzm
* created 2025/06/11 14:29:45
* @function: 
'''
import yaml
from typing import Iterable
import jsonlines


def get_yaml_data(yaml_file):
    # 打开yaml文件
    print("加载yaml文件:", yaml_file)
    with open(yaml_file, encoding="utf-8") as f:
        data = yaml.full_load(f.read())
    return data


def read_jsonl(path):
    content = []
    with jsonlines.open(path, "r") as json_file:
        for obj in json_file.iter(type=dict, skip_invalid=True):
            content.append(obj)
    return content
