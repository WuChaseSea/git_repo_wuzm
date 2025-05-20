# -*-coding:UTF-8 -*-
'''
* run.py
* @author wuzm
* created 2025/05/20 11:21:27
* @function: 
'''
import os
import json
import streamlit as st

from funciton_tools.util import functions, get_function_by_name
from model import llm, system_messages

system_messages.append({"role": "user",  "content": "帮我分析2024年上半年每日销售额的变化情况并绘制图表"})
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
        if fn_name == "plot_trend":
            fn_args['data'] = st.session_state.df_cache[-1]
        fn_res: str = json.dumps(get_function_by_name(fn_name)(**fn_args))

        system_messages.append({  # 以function作为role添加到message中去；
            "role": "function",
            "name": fn_name,
            "content": fn_res,
        })

import ipdb;ipdb.set_trace()
for responses in llm.chat(messages=system_messages, functions=functions):
    pass
system_messages.extend(responses)
print(system_messages[-1]['content'])
