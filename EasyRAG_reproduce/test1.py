# -*-coding:UTF-8 -*-
"""
* main.py
* @author wuzm
* created 2025/06/06 16:28:45
* @function: 主程序入口
"""
import os
from qwen_agent.llm import get_chat_model
llm = get_chat_model({
            "model": "qwen-max",
            "model_server": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "api_key": os.getenv("DASHSCOPE_API_KEY"),
        })
messages = [{
                'role': 'user',
                'content': "What's your name?"
            }]
responses = []
for responses in llm.chat(messages=messages,
                          stream=True):
    pass
print(responses[0]["content"])
