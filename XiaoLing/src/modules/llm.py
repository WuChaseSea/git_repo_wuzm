import os
import json
import re

from qwen_agent.llm import get_chat_model
from langchain_community.chat_models.tongyi import ChatTongyi
from llama_index.core import PromptTemplate

from src.modules.templates import SYSTEM_PROMPT, XIAOLING_PROMPT, INTENTION_PROMPT, PROVIDED_CHAT_PROMPT
from src.logger import logger

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
            user_input=user_input,
            chat_history=history if history else ""
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
    
    def intent_stream(self, user_message, history=None):
        mode, user_input = user_message.get("mode"), user_message.get("user_input")
        intent_prompt = PromptTemplate(INTENTION_PROMPT).format(
            mode=mode,
            user_input=user_input,
            chat_history=history if history else ""
        )
        messages = []
        messages.append(
            {
                "role": "user",
                "content": intent_prompt
            }
        )
        response = self.llm.chat(messages, stream=False)
        try:
            clean_response = response[0]["content"].strip('`').replace('json\n', '', 1)
            intent_data = json.loads(clean_response)
        except Exception as e:
            logger.error(f"Intent parse error: {e}")
            logger.info(f"Intent raw response: {response[0]['content']}")
            intent_data = {"intent": "chat"}

        return intent_data.get("intent", "chat")

    def provided_chat(self, mode, history):
        provide_chat_prompt = PromptTemplate(PROVIDED_CHAT_PROMPT).format(
            mode=mode,
            chat_history=history if history else ""
        )
        messages = []
        messages.append(
            {
                "role": "user",
                "content": provide_chat_prompt
            }
        )
        response = self.llm.chat(messages, stream=False)
        try:
            provided_data = re.sub(r"^```json\s*|\s*```$", "", response[0]["content"].strip())
            provided_data = json.loads(provided_data)
        except Exception as e:
            logger.error(f"Provided chat parse error: {e}")
            logger.info(f"Provided chat raw response: {response[0]['content']}")
            provided_data = {
                "text_1": "😮‍💨 我今天有点累",
                "text_2": "😤 有点烦同事",
                "text_3": "😶‍🌫️ 不想工作",
                "text_4": "💤 想摸鱼",
                "text_5": "✍️ 说点别的（自定义输入）"
            }
        return list(provided_data.values())


chat_llm = LLMPipeline()
