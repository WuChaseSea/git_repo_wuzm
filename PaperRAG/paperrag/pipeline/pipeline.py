# -*-coding:UTF-8 -*-
'''
* pipeline.py
* @author wuzm
* created 2025/06/11 19:06:52
* @function: 
'''
import os, sys
import re
from pathlib import Path
from tqdm import tqdm
import pickle
import asyncio, nest_asyncio
from qwen_agent.llm import get_chat_model

from llama_index.core import Settings, PromptTemplate, QueryBundle
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.embeddings.langchain import LangchainEmbedding
from qdrant_client import models

from ..custom.template import QA_TEMPLATE, MERGE_TEMPLATE, QA_TEMPLATE_EN
from ..custom.retrievers import QdrantRetriever, HybridRetriever, BM25Retriever
from ..custom.rerankers import SentenceTransformerRerank, LLMRerank
from .ingestion import read_data, build_vector_store, build_pipeline, build_qdrant_filters
from .ingestion import get_node_content as _get_node_content
from .rag import generation as _generation

nest_asyncio.apply()

def load_stopwords(path):
    with open(path, 'r', encoding='utf-8') as file:
        stopwords = set([line.strip() for line in file])
    return stopwords

from openai import OpenAI


class PaperRAGPipeline():
    def __init__(self, config):
        self.config = config
        asyncio.get_event_loop().run_until_complete(self.async_init())
    
    async def async_init(self):
        config = self.config
        self.llm_embed_type = config['llm_embed_type']
        self.re_only = config["re_only"]
        self.ans_refine_type = config['ans_refine_type']
        self.work_dir = config["work_dir"]
        print(f"Pipeline 初始化开始".center(60, "="))

        self.llm = get_chat_model({
            "model": config["llm_name"],
            "model_server": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "api_key": os.getenv("DASHSCOPE_API_KEY"),
        })
        # self.llm = OpenAI(
        #     base_url="https://api.ppinfra.com/v3/openai",
        #     api_key=os.getenv("PPIO_API_KEY")
        # )

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

        data_path = os.path.join(self.work_dir, config["data_path"])
        chunk_size = config["chunk_size"]
        chunk_overlap = config["chunk_overlap"]
        if not Path("documents.pkl").exists():
            data = read_data(data_path)
            with open("documents.pkl", "wb") as f:
                pickle.dump(data, f)
        else:
            with open("documents.pkl", "rb") as f:
                data = pickle.load(f)
        print(f"文档读入完成，一共有 {len(data)} 个文档.")

        vector_store = None
        collection_name = config["collection_name"]
        client, vector_store = build_vector_store(
            qdrant_url=config["qdrant_url"],
            cache_path=os.path.join(self.work_dir, config["cache_path"]),
            reindex=config["reindex"],
            collection_name=collection_name,
            vector_size=config["vector_size"]
        )
        collection_info = client.get_collection(
            collection_name=collection_name
        )
        pipeline = build_pipeline(
            self.llm, embedding, vector_store=vector_store, data_path=data_path,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        if collection_info.points_count == 0:
            # 暂时停止实时索引
            client.update_collection(
                collection_name=collection_name,
                optimizer_config=models.OptimizersConfigDiff(indexing_threshold=0),
            )
                
            nodes = pipeline.run(documents=data, show_progress=True, num_workers=1)
            # 恢复实时索引
            client.update_collection(
                collection_name=collection_name,
                optimizer_config=models.OptimizersConfigDiff(indexing_threshold=20000),
            )
            
            pipeline.persist(os.path.join(self.work_dir, f"pipeline_storage_{config['cache_path']}"))

            print(f"索引建立完成，一共有{len(nodes)}个节点")
        else:
            pipeline.load(os.path.join(self.work_dir, f"pipeline_storage_{config['cache_path']}"))
            nodes = pipeline.run(documents=data, show_progress=True, num_workers=1)
        
        if embedding is not None:
            f_topk_1 = config["f_topk_1"]
            self.dense_retriever = QdrantRetriever(vector_store, embedding, similarity_top_k=f_topk_1)
            print(f"创建{embedding}密集检索器成功")
        
        self.stp_words = load_stopwords(str(Path(config["work_dir"]) / "hit_stopwords.txt"))
        import jieba
        self.sparse_tk = jieba.Tokenizer()
        self.nodes = nodes
        
        f_topk_2 = config['f_topk_2']
        f_embed_type_2 = config['f_embed_type_2']
        bm25_type = config['bm25_type']
        self.sparse_retriever = BM25Retriever.from_defaults(
            nodes=self.nodes,
            tokenizer=self.sparse_tk,
            similarity_top_k=f_topk_2,
            stopwords=self.stp_words,
            embed_type=f_embed_type_2,
            bm25_type=bm25_type,
        )
        print("创建BM25稀疏检索器成功")
        # 创建检索器
        retrieval_type = config["retrieval_type"]
        if retrieval_type == 1:
            self.retriever = self.dense_retriever
        elif retrieval_type == 2:
            self.retriever = self.sparse_retriever
        elif retrieval_type == 3:
            f_topk = config['f_topk']
            self.retriever = HybridRetriever(
                dense_retriever=self.dense_retriever,
                sparse_retriever=self.sparse_retriever,
                retrieval_type=retrieval_type,  # 1-dense 2-sparse 3-hybrid
                topk=f_topk,
            )
            print("创建混合检索器成功")

        # 创建重排器
        self.reranker = None
        use_reranker = config['use_reranker']
        r_topk = config['r_topk']
        reranker_name = config['reranker_name']
        r_embed_type = config['r_embed_type']
        r_embed_bs = config['r_embed_bs']
        r_use_efficient = config['r_use_efficient']
        if use_reranker == 1:
            self.reranker = SentenceTransformerRerank(
                top_n=r_topk,
                model=reranker_name,
            )
            print(f"创建{reranker_name}重排器成功")
        elif use_reranker == 2:
            self.reranker = LLMRerank(
                top_n=r_topk,
                model=reranker_name,
                embed_bs=r_embed_bs,  # 控制重排器批大小，减小显存占用
                embed_type=r_embed_type,
                use_efficient=r_use_efficient,
            )
            print(f"创建{reranker_name}LLM重排器成功")

        # 创建node快速索引
        self.nodeid2idx = dict()
        for i, node in enumerate(self.nodes):
            self.nodeid2idx[node.node_id] = i
        
        self.path_retriever = None

        print("EasyRAGPipeline 初始化完成".center(60, "="))
    
    def build_prompt_template(self, qa_template):
        return PromptTemplate(qa_template)
    
    def build_filters(self, query):
        filters = None
        filter_dict = None
        if "paper_id" in query and query["paper_id"] != "":
            dir = query['paper_id']
            filters = build_qdrant_filters(
                dir=dir
            )
            filter_dict = {
                "file_path": dir
            }
        return filters, filter_dict
    
    def build_query_bundle(self, query_str):
        query_bundle = QueryBundle(query_str=query_str)
        return query_bundle

    def get_node_content(self, node) -> str:
        return _get_node_content(node, embed_type=self.llm_embed_type, nodes=self.nodes, nodeid2idx=self.nodeid2idx)

    async def generation(self, llm, fmt_qa_prompt):
        return await _generation(llm, fmt_qa_prompt)
    
    async def run(self, query: dict) -> dict:
        '''
        "query":"问题" #必填
        "document": "所属路径" #用于过滤文档，可选
        '''
        self.filters, self.filter_dict = self.build_filters(query)
        self.retriever.filters = self.filters
        self.retriever.filter_dict = self.filter_dict
        res = await self.generation_with_knowledge_retrieval(
            query_str=query["question"],
            hyde_query=query.get("hyde_query", "")
        )
        return res
    
    async def generation_with_knowledge_retrieval_four(
            self,
            query_str,
            hyde_query
    ):
        question_str = query_str.split('A.')[0].strip()
        answer_a = query_str.split('A.')[1].split('B.')[0].strip()
        answer_b = query_str.split('A.')[1].split('B.')[1].split('C.')[0].strip()
        answer_c = query_str.split('A.')[1].split('B.')[1].split('C.')[1].split('D.')[0].strip()
        answer_d = query_str.split('D.')[1].strip()
        query_bundle = self.build_query_bundle(question_str)
        answer_a_bundle = self.build_query_bundle(answer_a)
        answer_b_bundle = self.build_query_bundle(answer_b)
        answer_c_bundle = self.build_query_bundle(answer_c)
        answer_d_bundle = self.build_query_bundle(answer_d)
        nodes_query = await self.retriever.aretrieve(query_bundle)
        nodes_a = await self.retriever.aretrieve(answer_a_bundle)
        nodes_b = await self.retriever.aretrieve(answer_b_bundle)
        nodes_c = await self.retriever.aretrieve(answer_c_bundle)
        nodes_d = await self.retriever.aretrieve(answer_d_bundle)
        node_with_scores = []
        node_with_scores.extend(nodes_query)
        node_with_scores.extend(nodes_a)
        node_with_scores.extend(nodes_b)
        node_with_scores.extend(nodes_c)
        node_with_scores.extend(nodes_d)
        if self.path_retriever is not None:
            node_with_scores_path = await self.path_retriever.aretrieve(query_bundle)
        else:
            node_with_scores_path = []
        
        node_with_scores = HybridRetriever.fusion([
            node_with_scores,
            node_with_scores_path,
        ])
        if self.reranker:
            node_with_scores = self.reranker.postprocess_nodes(node_with_scores, query_bundle)

        contents = [self.get_node_content(node=node) for node in node_with_scores]
        context_str = "\n\n".join(
            [f"### 文档{i}: {content}" for i, content in enumerate(contents)]
        )
        if self.re_only:
            return {"answer": "", "nodes": node_with_scores, "contexts": contents}
        fmt_qa_prompt = self.qa_template.format(
            context_str=context_str, query_str=query_str
        )
        ret = await self.generation(self.llm, fmt_qa_prompt)
        if self.ans_refine_type == 1:
            fmt_merge_prompt = self.merge_template.format(
                context_str=contents[0], query_str=query_str, answer_str=ret.text
            )
            ret = await self.generation(self.llm, fmt_merge_prompt)
        elif self.ans_refine_type == 2:
            ret.text = ret.text + "\n\n" + contents[0]
        return {"answer": ret, "nodes": node_with_scores, "contexts": contents}


        

    async def generation_with_knowledge_retrieval(
            self,
            query_str: str,
            hyde_query: str = ""
    ):
        query_bundle = self.build_query_bundle(query_str + hyde_query)
        # node_with_scores = await self.sparse_retriever.aretrieve(query_bundle)
        
        # node_with_scores = self.dense_retriever.retrieve(query_bundle)
        node_with_scores = await self.retriever.aretrieve(query_bundle)
        
        if self.path_retriever is not None:
            node_with_scores_path = await self.path_retriever.aretrieve(query_bundle)
        else:
            node_with_scores_path = []
        
        node_with_scores = HybridRetriever.fusion([
            node_with_scores,
            node_with_scores_path,
        ])
        if self.reranker:
            node_with_scores = self.reranker.postprocess_nodes(node_with_scores, query_bundle)

        contents = [self.get_node_content(node=node) for node in node_with_scores]
        context_str = "\n\n".join(
            [f"### 文档{i}: {content}" for i, content in enumerate(contents)]
        )
        if self.re_only:
            return {"answer": "", "nodes": node_with_scores, "contexts": contents}
        fmt_qa_prompt = self.qa_template.format(
            context_str=context_str, query_str=query_str
        )
        ret = await self.generation(self.llm, fmt_qa_prompt)
        if self.ans_refine_type == 1:
            fmt_merge_prompt = self.merge_template.format(
                context_str=contents[0], query_str=query_str, answer_str=ret.text
            )
            ret = await self.generation(self.llm, fmt_merge_prompt)
        elif self.ans_refine_type == 2:
            ret.text = ret.text + "\n\n" + contents[0]
        return {"answer": ret, "nodes": node_with_scores, "contexts": contents}
