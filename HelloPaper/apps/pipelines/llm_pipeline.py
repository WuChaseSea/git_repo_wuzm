import os
from pathlib import Path

from qwen_agent.llm import get_chat_model
from llama_index.core import PromptTemplate
from llama_index.core.base.llms.types import CompletionResponse
from langchain_community.chat_models.tongyi import ChatTongyi

from apps.base import Document
from apps.pipelines.templates import SYSTEM_PROMPT, DEFAULT_QA_TEXT_PROMPT
from .mindmap_pipeline import MindmapPipeline
from .citation_pipeline import CitationPipeline


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
        self.llm_chat = ChatTongyi(model="qwen-plus", temperature=1.0)
        self.system_prompt = SYSTEM_PROMPT
        self.build_prompt_template(mode="text")
        self.mindmap_pipeline = MindmapPipeline(self.llm)
        self.citation_pipeline = CitationPipeline(self.llm_chat)
    
    def build_prompt_template(self, mode, desc=None, prompt=None):
        if mode == "text":
            if desc is None:
                self.qa_template_text = PromptTemplate(DEFAULT_QA_TEXT_PROMPT)
            else:
                template_tmp = PromptTemplate(prompt)
                var_name = f"template_{desc}_{mode}"
                setattr(self, var_name, template_tmp)
    
    def stream(self, question, history, context):
        qa_prompt = self.qa_template_text.format(
            lang="English",
            context=context,
            question=question
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
                "content": qa_prompt
            }
        )

        try:
            print(f"Trying LLM streaming:")
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
                yield Document(channel="chat", content=now_output)
            print(f"LLM streaming end.")
        except NotImplementedError:
            print(f"Stream error.")
            for outputs in self.llm.chat(messages=messages):
                pass
            output = outputs[0]["content"]
            yield Document(channel="chat", content=output)
        
        mindmap = self.mindmap_pipeline.run(context=context, question=question)
        # citation = self.citation_pipeline.run(context=context, question=question)
        
        answer = Document(
            text=output,
            metadata={
                "mindmap": mindmap
            }
        )

        return answer
