# -*-coding:UTF-8 -*-
'''
* pipeline.py
* @author wuzm
* created 2025/06/11 19:06:52
* @function: 
'''
import os, sys
import re
import numpy as np
from pathlib import Path
from tqdm import tqdm
import pickle
import asyncio, nest_asyncio
from qwen_agent.llm import get_chat_model

from llama_index.core import Settings, PromptTemplate, QueryBundle
from langchain_community.embeddings import HuggingFaceBgeEmbeddings, SentenceTransformerEmbeddings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.embeddings.langchain import LangchainEmbedding
from qdrant_client import models
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import IndexNode
from llama_index.core import VectorStoreIndex
from llama_index.core.retrievers import RecursiveRetriever
from sentence_transformers import SentenceTransformer
import sentence_transformers

class SentenceTransformerMy(object):
    
    encode_kwargs = dict()
    # See also the Sentence Transformer documentation: https://sbert.net/docs/package_reference/SentenceTransformer.html#sentence_transformers.SentenceTransformer.encode"""
    multi_process: bool = False
    """Run encode() on multiple GPUs."""
    show_progress: bool = False
    """Whether to show a progress bar."""
    
    def __init__(self, model_path, **kwargs):
        self.client = SentenceTransformer(model_path, **kwargs)
    
    def embed_documents(self, texts):
            """Compute doc embeddings using a HuggingFace transformer model.

            Args:
                texts: The list of texts to embed.

            Returns:
                List of embeddings, one for each text.
            """

            texts = list(map(lambda x: x.replace("\n", " "), texts))
            if self.multi_process:
                pool = self.client.start_multi_process_pool()
                embeddings = self.client.encode_multi_process(texts, pool)
                sentence_transformers.SentenceTransformer.stop_multi_process_pool(pool)
            else:
                embeddings = self.client.encode(
                    texts, show_progress_bar=self.show_progress, **self.encode_kwargs
                )

            return embeddings.tolist()
        
    def embed_query(self, text: str):
        """Compute query embeddings using a HuggingFace transformer model.

        Args:
            text: The text to embed.

        Returns:
            Embeddings for the text.
        """
        return self.embed_documents([text])[0]


from ..custom.template import QA_TEMPLATE, MERGE_TEMPLATE, HyDE_TEMPLATE, QA_TEMPLATE_EN, QA_TEMPLATE_0, QA_TEMPLATE_1, QA_TEMPLATE_2, QA_TEMPLATE_3, QA_TEMPLATE_4, QA_TEMPLATE_5
from ..custom.retrievers import QdrantRetriever, HybridRetriever, BM25Retriever
from ..custom.rerankers import SentenceTransformerRerank, LLMRerank
from .ingestion import read_data, build_vector_store, build_pipeline, build_qdrant_filters
from .ingestion import get_node_content as _get_node_content
from .rag import generation as _generation
from ..utils.rewrite_query import rewrite_query, generate_multi_perspective_queries

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
            'generate_cfg': {
                'temperature': 0.0
            }
        })

        self.qa_template = self.build_prompt_template(QA_TEMPLATE)
        self.merge_template = self.build_prompt_template(MERGE_TEMPLATE)
        self.hyde_template = self.build_prompt_template(HyDE_TEMPLATE)
        
        model_name = config["embedding_name"]
        # embedding = SentenceTransformerMy(model_name)
        # import ipdb;ipdb.set_trace()
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
        data = read_data(data_path)
        # if not Path("documents.pkl").exists():
        #     data = read_data(data_path)
        #     with open("documents.pkl", "wb") as f:
        #         pickle.dump(data, f)
        # else:
        #     with open("documents.pkl", "rb") as f:
        #         data = pickle.load(f)
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

        # sub_chunk_sizes = [64, 128, 256]
        # sub_node_parsers = [
        #     SentenceSplitter(chunk_size=c, chunk_overlap=20) for c in sub_chunk_sizes
        # ]

        # all_nodes = []
        # for base_node in self.nodes:
        #     for n in sub_node_parsers:
        #         sub_nodes = n.get_nodes_from_documents([base_node])
        #         sub_inodes = [
        #             IndexNode.from_text_node(sn, base_node.node_id) for sn in sub_nodes
        #         ]
        #         all_nodes.extend(sub_inodes)

        #     # also add original node to node
        #     original_node = IndexNode.from_text_node(base_node, base_node.node_id)
        #     all_nodes.append(original_node)
        # all_nodes_dict = {n.node_id: n for n in all_nodes}
        # vector_index_chunk = VectorStoreIndex(all_nodes, embed_model=bge_embeddings)
        # vector_retriever_chunk = vector_index_chunk.as_retriever(similarity_top_k=2*f_topk_1)
        # self.retriever_chunk = RecursiveRetriever(
        #     "vector",
        #     retriever_dict={"vector": vector_retriever_chunk},
        #     node_dict=all_nodes_dict,
        #     verbose=True,
        # )
        
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
        self.retrieval_type = config["retrieval_type"]
        if self.retrieval_type == 1:
            self.retriever = self.dense_retriever
        elif self.retrieval_type == 2:
            self.retriever = self.sparse_retriever
        elif self.retrieval_type == 3:
            f_topk = config['f_topk']
            self.retriever = HybridRetriever(
                dense_retriever=self.dense_retriever,
                sparse_retriever=self.sparse_retriever,
                retrieval_type=self.retrieval_type,  # 1-dense 2-sparse 3-hybrid
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
            target_dir = Path(self.config["work_dir"]) / "papar_QA_dataset/papers" / dir
            pdf_filenames = [f.name for f in target_dir.glob("*.pdf")]
            pdf_filenames = [f for f in pdf_filenames if not f.startswith(".")][0]
            filters = build_qdrant_filters(
                dir=dir
            )
            filter_dict = {
                "file_path": Path(pdf_filenames).stem
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
            hyde_query=query.get("hyde_query", ""),
            template_id=query["correct_answer"]
        )
        return res
    
    def rewrite_query(self, query_str):
        question_str = query_str.split('A.')[0].strip()
        answer_a = query_str.split('A.')[1].split('B.')[0].strip()
        answer_b = query_str.split('A.')[1].split('B.')[1].split('C.')[0].strip()
        answer_c = query_str.split('A.')[1].split('B.')[1].split('C.')[1].split('D.')[0].strip()
        answer_d = query_str.split('D.')[1].strip()

        # qa_list = [
        #     {
        #         "question": question_str,
        #         "options": ['A. '+answer_a, 'B. '+answer_b, 'C. '+answer_c, 'D. '+answer_d]
        #     }
        # ]
        # output = generate_multi_perspective_queries(qa_list)[0]
        # rewrite_result = output["multi_view_query"]

        options = [answer_a, answer_b, answer_c, answer_d]
        rewrite_result = rewrite_query(question_str, options, mode="default")
        return rewrite_result
    
    async def generation_with_knowledge_retrieval_four(
            self,
            query_str,
            hyde_query,
            template_id
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
        nodes_query = self.dense_retriever.retrieve(query_bundle)
        nodes_a = self.dense_retriever.retrieve(answer_a_bundle)
        nodes_b = self.dense_retriever.retrieve(answer_b_bundle)
        nodes_c = self.dense_retriever.retrieve(answer_c_bundle)
        nodes_d = self.dense_retriever.retrieve(answer_d_bundle)
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
            hyde_query: str = "",
            template_id: int = 3
    ):
        query_bundle = self.build_query_bundle(query_str + hyde_query)
        # node_with_scores = await self.sparse_retriever.aretrieve(query_bundle)
        query_bundle_rewrite = self.build_query_bundle(self.rewrite_query(query_str) + hyde_query)
        hyde_prompt = self.hyde_template.format(
            question=query_str
        )
        ret_hyde = await self.generation(self.llm, hyde_prompt)
        query_bundle_hyde = self.build_query_bundle(ret_hyde)
        if self.retrieval_type == 1:
            node_with_scores = self.dense_retriever.retrieve(query_bundle)
            node_with_scores_rewrite = self.dense_retriever.retrieve(query_bundle_rewrite)
            node_with_scores_hyde = self.dense_retriever.retrieve(query_bundle_hyde)
            # node_with_scores = [i for i in node_with_scores if i.score > 0.65]
            # node_with_scores_rewrite = [i for i in node_with_scores_rewrite if i.score > 0.65]
            node_scores = [i.score for i in node_with_scores]
            node_scores_write = [i.score for i in node_with_scores_rewrite]
            node_scores_hyde = [i.score for i in node_with_scores_hyde]
            origin = False
            if np.mean(node_scores_write) < np.mean(node_scores):
            # if node_scores_write[0] < node_scores[0]:
                origin = True
            print(f"origin score: {node_scores}")
            print(f"rewrite score: {node_scores_write}")
            print(f"hyde score: {node_scores_hyde}")
        elif self.retrieval_type == 2:
            node_with_scores = await self.sparse_retriever.aretrieve(query_bundle)
        else:
            node_with_scores = await self.retriever.aretrieve(query_bundle)
            node_with_scores_rewrite = await self.retriever.aretrieve(query_bundle_rewrite)
            node_scores = [i.score for i in node_with_scores]
            node_scores_write = [i.score for i in node_with_scores_rewrite]
            origin = False
            if node_scores_write[0] < node_scores[0]:
                origin = True
            print(f"origin score: {node_scores}")
            print(f"rewrite score: {node_scores_write}")
        if self.path_retriever is not None:
            node_with_scores_path = await self.path_retriever.aretrieve(query_bundle)
        else:
            node_with_scores_path = []
        if origin:
            node_with_scores = HybridRetriever.fusion([
                node_with_scores,
                node_with_scores_hyde,
            ])
        else:
            node_with_scores = HybridRetriever.fusion([
                node_with_scores_rewrite,
                node_with_scores_hyde,
            ])
        
        if self.reranker:
            node_with_scores = self.reranker.postprocess_nodes(node_with_scores, query_bundle)

        contents = [self.get_node_content(node=node) for node in node_with_scores]
        context_str = "\n\n".join(
            [f"### 文档{i}: {content}" for i, content in enumerate(contents)]
        )
        if self.re_only:
            return {"answer": "", "nodes": node_with_scores, "contexts": contents}
        template_id = int(template_id)
        # if template_id == 0:
        #     self.qa_template = self.build_prompt_template(QA_TEMPLATE_0)
        # elif template_id == 1:
        #     self.qa_template = self.build_prompt_template(QA_TEMPLATE_1)
        # elif template_id == 2:
        #     self.qa_template = self.build_prompt_template(QA_TEMPLATE_2)
        # elif template_id == 4:
        #     self.qa_template = self.build_prompt_template(QA_TEMPLATE_4)
        # elif template_id == 5:
        #     self.qa_template = self.build_prompt_template(QA_TEMPLATE_5)
        # else:
        #     self.qa_template = self.build_prompt_template(QA_TEMPLATE_3)
        
        fmt_qa_prompt = self.qa_template.format(
            context_str=context_str, query_str=query_str
        )
        ret = await self.generation(self.llm, fmt_qa_prompt)
        # ret = None
        if self.ans_refine_type == 1:
            fmt_merge_prompt = self.merge_template.format(
                context_str=contents[0], query_str=query_str, answer_str=ret.text
            )
            ret = await self.generation(self.llm, fmt_merge_prompt)
        elif self.ans_refine_type == 2:
            ret.text = ret.text + "\n\n" + contents[0]
        return {"answer": ret, "nodes": node_with_scores, "contexts": contents}
    
