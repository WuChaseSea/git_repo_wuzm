# -*-coding:UTF-8 -*-
'''
* pipeline.py
* @author wuzm
* created 2025/06/11 19:06:52
* @function: 
'''
import os
import asyncio, nest_asyncio
from qwen_agent.llm import get_chat_model

from llama_index.core import Settings, PromptTemplate
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.embeddings.langchain import LangchainEmbedding

from ..custom.template import QA_TEMPLATE, MERGE_TEMPLATE
from .injection import read_data

nest_asyncio.apply()


class PaperRAGPipeline():
    def __init__(self, config):
        self.config = config
        asyncio.get_event_loop().run_until_complete(self.async_init())
    
    async def async_init(self):
        config = self.config
        print(f"Pipeline 初始化开始".center(60, "="))
        self.llm = get_chat_model({
            "model": "qwen-max",
            "model_server": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "api_key": os.getenv("DASHSCOPE_API_KEY"),
        })
        self.qa_template = self.build_prompt_template(QA_TEMPLATE)
        self.merge_template = self.build_prompt_template(MERGE_TEMPLATE)

        model_name = config["embedding_name"]
        model_kwargs = {'device': 'cpu'}
        encode_kwargs = {'normalize_embeddings': False}
        bge_embeddings = HuggingFaceBgeEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )
        embedding = LangchainEmbedding(bge_embeddings)
        Settings.embed_model = embedding
        print(f"Embddding 创建完成.")

        data_path = config["data_path"]
        chunk_size = config["chunk_size"]
        chunk_overlap = config["chunk_overlap"]
        data = read_data(data_path)
        print(f"文档读入完成，一共有 {len(data)} 个文档.")
        import ipdb;ipdb.set_trace()
    
    def build_prompt_template(self, qa_template):
        return PromptTemplate(qa_template)
