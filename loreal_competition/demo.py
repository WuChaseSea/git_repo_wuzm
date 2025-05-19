# -*-coding:UTF-8 -*-
'''
* demo.py
* @author wuzm
* created 2025/05/19 11:23:12
* @function: data analysis demo
'''
import os
import json
import re
import sqlite3
import pandas as pd
from openai import OpenAI
# import streamlit as st
from transformers import AutoTokenizer
from qwen_agent.llm import get_chat_model


system_messages = [
    {"role": "system", "content": "你是一个数据分析师，现在根据用户的要求提供相应的销售数据分析结果。当用户提出的问题没有对应的tools解决时告知用户并介绍你能解决的问题。"},
    {"role": "user",  "content": "帮我分析第一周每日销售额的变化情况"},
]
# ------------------------------------ 模型、数据初始化部分 ------------------------------------ #
# @st.cache_resource
def get_qwen_model():
    llm = get_chat_model({
        "model": "qwen-max",
        "model_server": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "api_key": os.getenv("DASHSCOPE_API_KEY"),
    })
    return llm

# ------------------------------------ 声明LLM能调用的函数 ------------------------------------ #
# 注意：
# 此部分的函数注释是一种固定格式，用于帮助LLM理解函数的功能
def daily_sales():
    """按日期统计每日销售额，并打印到屏幕上

    Args:
        None

    Returns:
        包含每日销售额的字典，键为日期，值为销售额
    """
    query = """
    SELECT order_date, SUM(sales) AS total_sales
    FROM new_fact_order_detail
    GROUP BY order_date
    ORDER BY order_date;
    """
    conn = sqlite3.connect('data/order_database.db')
    df = pd.read_sql_query(query, conn)
    # st.dataframe(df)
    return df.set_index('order_date')['total_sales'].to_dict()

def sales_by_brand():
    """按品牌统计销售额，并打印到屏幕上

    Args:
        None

    Returns:
        包含各品牌销售额的字典，键为品牌代码，值为销售额
    """
    conn = sqlite3.connect('data/order_database.db')
    query = """
    SELECT brand_code, SUM(sales) AS total_sales
    FROM new_fact_order_detail
    GROUP BY brand_code
    ORDER BY total_sales DESC;
    """
    conn = sqlite3.connect('data/order_database.db')
    df = pd.read_sql_query(query, conn)
    # st.dataframe(df)
    return df.set_index('brand_code')['total_sales'].to_dict()

def orders_by_channel():
    """按渠道统计订单数量，并打印到屏幕上

    Args:
        None

    Returns:
        包含各渠道订单数量的字典，键为渠道名称，值为订单数量
    """
    query = """
    SELECT channel, COUNT(order_no) AS order_count
    FROM new_fact_order_detail
    GROUP BY channel
    ORDER BY order_count DESC;
    """
    conn = sqlite3.connect('data/order_database.db')
    df = pd.read_sql_query(query, conn)
    # st.dataframe(df)
    return df.set_index('channel')['order_count'].to_dict()

def get_function_by_name(name):
    if name == "daily_sales":
        return daily_sales
    if name == "sales_by_brand":
        return sales_by_brand
    if name == "orders_by_channel":
        return orders_by_channel

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "daily_sales",
            "description": "按日期统计每日销售额。",
            "parameters": {
                "type": "object",
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "sales_by_brand",
            "description": "按品牌统计销售额。",
            "parameters": {
                "type": "object",
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "orders_by_channel",
            "description": "按渠道统计订单数量。",
            "parameters": {
                "type": "object",
            },
        },
    },
]
functions = [tool["function"] for tool in TOOLS]
# ------------------------------------ LLM调用函数和回复逻辑 ------------------------------------ #

llm = get_qwen_model()

for responses in llm.chat(
    messages=system_messages,
    functions=functions,
    extra_generate_cfg=dict(parallel_function_calls=True),
):
    pass
system_messages.extend(responses)

for message in responses:

    if fn_call := message.get("function_call", None):
        fn_name: str = fn_call['name']
        fn_args: dict = json.loads(fn_call["arguments"])

        fn_res: str = json.dumps(get_function_by_name(fn_name)(**fn_args))

        system_messages.append({  # 以function作为role添加到message中去；
            "role": "function",
            "name": fn_name,
            "content": fn_res,
        })

for responses in llm.chat(messages=system_messages, functions=functions):
    pass
system_messages.extend(responses)
print(system_messages[-1]['content'])

# if __name__ == '__main__':
#     daily_sales()

    # st.title("Data Analysis Demo")
    # st.text("This is a Demo for data analysis......")
    # # 初始提示词
    # if "messages" not in st.session_state:
    #     st.session_state.messages = [{"role": "system", "content": "你是一个数据分析师，现在根据用户的要求提供相应的销售数据分析结果。当用户提出的问题没有对应的tools解决时告知用户并介绍你能解决的问题。"}]

    # # 显示聊天历史记录
    # for message in st.session_state.messages:
    #     if message["role"]=='system':   # 不打印提示词
    #         continue
    #     with st.chat_message(message["role"]):
    #         st.markdown(message["content"])

    # # 接受用户输入
    # if prompt := st.chat_input("按日期统计每日销售额"):
    #     # 将用户输入添加进聊天历史记录
    #     st.session_state.messages.append({"role": "user", "content": prompt})
    #     # 将用户输入打印到屏幕上
    #     with st.chat_message("user"):
    #         st.markdown(prompt)
        
    #     # 打印模型输出到屏幕上
    #     with st.chat_message("assistant"):
    #         response = st.markdown(qwen_func_response())  # 获取模型输出
