# -*-coding:UTF-8 -*-
'''
* funciton_test.py
* @author wuzm
* created 2025/05/19 17:16:30
* @function: qwen函数调用的测试文件，以官网为例，https://qwen.readthedocs.io/zh-cn/latest/framework/function_call.html#id5
'''
import json

# ------------------------------------ 声明LLM能调用的函数 ------------------------------------ #
def get_current_temperature(location: str, unit: str = "celsius"):
    """Get current temperature at a location.

    Args:
        location: The location to get the temperature for, in the format "City, State, Country".
        unit: The unit to return the temperature in. Defaults to "celsius". (choices: ["celsius", "fahrenheit"])

    Returns:
        the temperature, the location, and the unit in a dict
    """
    return {
        "temperature": 26.1,
        "location": location,
        "unit": unit,
    }


def get_temperature_date(location: str, date: str, unit: str = "celsius"):
    """Get temperature at a location and date.

    Args:
        location: The location to get the temperature for, in the format "City, State, Country".
        date: The date to get the temperature for, in the format "Year-Month-Day".
        unit: The unit to return the temperature in. Defaults to "celsius". (choices: ["celsius", "fahrenheit"])

    Returns:
        the temperature, the location, the date and the unit in a dict
    """
    return {
        "temperature": 25.9,
        "location": location,
        "date": date,
        "unit": unit,
    }

def get_function_by_name(name):
    if name == "get_current_temperature":
        return get_current_temperature
    if name == "get_temperature_date":
        return get_temperature_date

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_temperature",
            "description": "Get current temperature at a location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": 'The location to get the temperature for, in the format "City, State, Country".',
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": 'The unit to return the temperature in. Defaults to "celsius".',
                    },
                },
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_temperature_date",
            "description": "Get temperature at a location and date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": 'The location to get the temperature for, in the format "City, State, Country".',
                    },
                    "date": {
                        "type": "string",
                        "description": 'The date to get the temperature for, in the format "Year-Month-Day".',
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": 'The unit to return the temperature in. Defaults to "celsius".',
                    },
                },
                "required": ["location", "date"],
            },
        },
    },
]

# ------------------------------------ 准备模型 ------------------------------------ #
MESSAGES = [
    {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant.\n\nCurrent Date: 2024-09-30"},
    {"role": "user",  "content": "What's the temperature in San Francisco now? How about tomorrow?"},
]
import os
from qwen_agent.llm import get_chat_model

llm = get_chat_model({
    "model": "qwen-max",
    "model_server": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "api_key": os.getenv("DASHSCOPE_API_KEY"),
})

messages = MESSAGES[:]
# [
#    {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant.\n\nCurrent Date: 2024-09-30"},
#    {"role": "user", "content": "What's the temperature in San Francisco now? How about tomorrow?"}
# ]

functions = [tool["function"] for tool in TOOLS]

# ------------------------------------ 工具调用与工具结果 ------------------------------------ #
for responses in llm.chat(
    messages=messages,
    functions=functions,
    extra_generate_cfg=dict(parallel_function_calls=True),
):
    pass
messages.extend(responses)

for message in responses:
    if fn_call := message.get("function_call", None):
        fn_name: str = fn_call['name']
        fn_args: dict = json.loads(fn_call["arguments"])
        
        fn_res: str = json.dumps(get_function_by_name(fn_name)(**fn_args))

        messages.append({  # 以function作为role添加到message中去；
            "role": "function",
            "name": fn_name,
            "content": fn_res,
        })

for responses in llm.chat(messages=messages, functions=functions):
    pass
messages.extend(responses)
print(messages[-1]['content'])
# for message in messages:
#     print(message)