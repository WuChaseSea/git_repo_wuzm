import os

from qwen_agent.llm import get_chat_model
from langchain_community.chat_models.tongyi import ChatTongyi


class LLMPipeline():

    def __init__(self):
        self.llm = get_chat_model({
            "model": "qwen-plus-2025-01-25",
            "model_server": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "api_key": os.getenv("DASHSCOPE_API_KEY"),
            'generate_cfg': {
                'temperature': 0.0
            }
        })
