import os

from qwen_agent.llm import get_chat_model
from langchain_community.chat_models.tongyi import ChatTongyi
from llama_index.core import PromptTemplate

from src.modules.templates import SYSTEM_PROMPT, XIAOLING_PROMPT


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
        self.system_prompt = SYSTEM_PROMPT
    
    def stream(self, user_message, user_prompt=None, history=None):
        mode, user_input = user_message.get("mode"), user_message.get("user_input")
        xiaoling_prompt = PromptTemplate(XIAOLING_PROMPT).format(
            mode=mode,
            user_input=user_input
        )
        messages = []
        if self.system_prompt:
            messages.append(
                {
                    "role": "system",
                    "content": self.system_prompt
                }
            )
        messages.append(
            {
                "role": "user",
                "content": xiaoling_prompt
            }
        )
        try:
            output = ""
            before_output = None
            for out_msg in self.llm.chat(messages, stream=True):
                now_output = out_msg[0]["content"]
                if before_output:
                    now_output = now_output[len(before_output):]
                    before_output += now_output
                else:
                    before_output = now_output
                output += now_output
                yield now_output
            return output
        except Exception as e:
            print(f"LLM stream error: {e}")
            return None


chat_llm = LLMPipeline()
