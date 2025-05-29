# -*-coding:UTF-8 -*-
'''
* test.py
* @author wuzm
* created 2025/05/19 11:02:24
* @function: test function
'''
import os, sys
sys.path.append('./')
import pandas as pd
from funciton_tools.trend_analysis import analyze_trend, plot_trend, read_table
from llm_service import decide_questions

def attribute_info(df):
    """
    Obtain the attributes, types, and head information of the DataFrame.
    """
    attributes = df.columns.tolist()
    dtypes_df = df.dtypes
    types_info = "\n".join([f"{index}:{dtype}" for index, dtype in dtypes_df.items()])
    head_info = df.head(10).to_csv()

    return attributes, types_info, head_info

if __name__ == "__main__":
    data = read_table()
    attributes_info, types_info, head_info = attribute_info(data)
    print(attributes_info)
    print(f"***** types_info *****")
    print(types_info)
    print(f"***** head_info *****")
    print(head_info)

    prob_questions = decide_questions(attributes_info, head_info)
    print(f"您可能想分析的问题有：")
    print(prob_questions)
