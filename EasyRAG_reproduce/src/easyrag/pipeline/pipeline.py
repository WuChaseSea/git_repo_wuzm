import os
import asyncio, nest_asyncio
from qwen_agent.llm import get_chat_model
from llama_index.core import Settings, PromptTemplate
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from qdrant_client import models

from ..custom.template import QA_TEMPLATE, MERGE_TEMPLATE
from .injestion import read_data, build_preprocess_pipeline, build_vector_store, build_pipeline

nest_asyncio.apply()


class EasyRAGPipeline:
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
        print(f"LLM model 创建完成.")

        model_name = config["embedding_name"]
        model_kwargs = {'device': 'cpu'}
        encode_kwargs = {'normalize_embeddings': False}
        embedding = HuggingFaceBgeEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )
        Settings.embed_model = embedding
        print(f"Embddding 创建完成.")

        data_path = config["data_path"]
        chunk_size = config["chunk_size"]
        chunk_overlap = config["chunk_overlap"]
        data = read_data(data_path)
        print(f"文档读入完成，一共有 {len(data)} 个文档.")
        vector_store = None

        collection_name = config["collection_name"]
        client, vector_store = await build_vector_store(
            qdrant_url=config["qdrant_url"],
            cache_path=config["cache_path"],
            reindex=config["reindex"],
            collection_name=collection_name,
            vector_size=config["vector_size"]
        )
        collection_info = await client.get_collection(
            collection_name=collection_name
        )
        if collection_info.points_count == 0:
            pipeline = build_pipeline(
                self.llm, embedding, vector_store=vector_store, data_path=data_path,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
            # 暂时停止实时索引
            await client.update_collection(
                collection_name=collection_name,
                optimizer_config=models.OptimizersConfigDiff(indexing_threshold=0),
            )
            nodes = await pipeline.arun(documents=data, show_progress=True, num_workers=1)
            # 恢复实时索引
            await client.update_collection(
                collection_name=collection_name,
                optimizer_config=models.OptimizersConfigDiff(indexing_threshold=20000),
            )
            print(f"索引建立完成，一共有{len(nodes)}个节点")

        split_type = config["split_type"]
        preprocess_pipeline = build_preprocess_pipeline(
            data_path,
            chunk_size,
            chunk_overlap,
            split_type
        )
        nodes_ = await preprocess_pipeline.arun(documents=data, show_progress=True, num_workers=1)
        print(f"索引已建立，一共有{len(nodes_)}个节点")

    def build_prompt_template(self, qa_template):
        return PromptTemplate(qa_template)
