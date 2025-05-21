# -*-coding:UTF-8 -*-
'''
* model.py
* @author wuzm
* created 2025/05/20 11:28:11
* @function: LLM模型构建
'''
import os, json
import streamlit as st
from qwen_agent.llm import get_chat_model

from funciton_tools.util import functions, get_function_by_name

llm = get_chat_model({
    "model": "qwen-max",
    "model_server": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "api_key": os.getenv("DASHSCOPE_API_KEY"),
})


def llm_chat(message):
    st.session_state.outputs = []
    st.session_state.system_messages.append(message)
    for responses in llm.chat(
        messages=st.session_state.system_messages,
        functions=functions,
        extra_generate_cfg=dict(parallel_function_calls=True),
    ):
        pass
    st.session_state.system_messages.extend(responses)

    # st.session_state.outputs = []
    for message in responses:

        if fn_call := message.get("function_call", None):
            fn_name: str = fn_call['name']
            fn_args: dict = json.loads(fn_call["arguments"])
            
            if fn_name == "plot_trend":
                fn_args['data'] = st.session_state.df_cache[-1]
            # fn_res: str = json.dumps(get_function_by_name(fn_name)(**fn_args))
            result = get_function_by_name(fn_name)(**fn_args)

            st.session_state.system_messages.append({  # 以function作为role添加到message中去；
                "role": "function",
                "name": fn_name,
                "content": json.dumps({f'{fn_name}': 'success'}),
            })
            st.session_state.outputs.append(result)
    
    for responses in llm.chat(messages=st.session_state.system_messages, functions=functions):
        pass
    st.session_state.system_messages.extend(responses)
    return st.session_state.system_messages[-1]['content']
