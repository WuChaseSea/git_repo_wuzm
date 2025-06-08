import os
import asyncio, nest_asyncio
from qwen_agent.llm import get_chat_model
from llama_index.core import Settings, PromptTemplate, StorageContext, QueryBundle
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.core.storage.docstore import SimpleDocumentStore
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.embeddings.langchain import LangchainEmbedding
from qdrant_client import models

from ..custom.template import QA_TEMPLATE, MERGE_TEMPLATE
from ..custom.retrievers import QdrantRetriever, BM25Retriever, HybridRetriever
from ..custom.hierarchical import get_leaf_nodes
from .injestion import read_data, build_preprocess_pipeline, build_vector_store, build_pipeline, build_qdrant_filters
from .injestion import get_node_content as _get_node_content
from .rag import generation as _generation


def load_stopwords(path):
    with open(path, 'r', encoding='utf-8') as file:
        stopwords = set([line.strip() for line in file])
    return stopwords


nest_asyncio.apply()


class EasyRAGPipeline:
    def __init__(self, config):
        self.config = config
        asyncio.get_event_loop().run_until_complete(self.async_init())

    async def async_init(self):
        config = self.config
        print(f"Pipeline 初始化开始".center(60, "="))
        self.rerank_fusion_type = config['rerank_fusion_type']
        self.llm_embed_type = config['llm_embed_type']
        self.re_only = config["re_only"]
        self.ans_refine_type = config['ans_refine_type']
        self.hyde = config['hyde']
        self.hyde_merging = config['hyde_merging']
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

        import pickle
        CACHE_FILE = f"cache/{collection_name}_cached_nodes.pkl"

        if collection_info.points_count == 0:
            if os.path.exists(CACHE_FILE):
                print("加载本地缓存的 nodes")
                with open(CACHE_FILE, "rb") as f:
                    nodes = pickle.load(f)
                print(f"已加载{len(nodes)}个节点")
                for node in nodes:
                    vector_store.add(node.get_embedding())  # 添加到 Qdrant
            else:
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
                import ipdb;ipdb.set_trace()
                nodes = await pipeline.run(documents=data, show_progress=True, num_workers=4)
                nodes = await pipeline.arun(documents=data, show_progress=True, num_workers=1)
                with open(CACHE_FILE, "wb") as f:
                    pickle.dump(nodes, f)
                print(f"索引建立完成，已缓存{len(nodes)}个节点")
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

        if embedding is not None:
            f_topk_1 = config["f_topk_1"]
            self.dense_retriever = QdrantRetriever(vector_store, embedding, similarity_top_k=f_topk_1)
            print(f"创建{embedding}密集检索器成功")

        self.stp_words = load_stopwords("/Users/wuzm/Documents/CodeRepository/git_repo_wuzm/EasyRAG/data/hit_stopwords.txt")
        import jieba
        self.sparse_tk = jieba.Tokenizer()
        if split_type == 1:
            self.nodes = get_leaf_nodes(nodes_)
            print("叶子节点数量:", len(self.nodes))
            docstore = SimpleDocumentStore()
            docstore.add_documents(self.nodes)
            storage_context = StorageContext.from_defaults(docstore=docstore)
        else:
            self.nodes = nodes_
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

        f_topk_3 = config['f_topk_3']
        if f_topk_3 != 0:
            self.path_retriever = BM25Retriever.from_defaults(
                nodes=self.nodes,
                tokenizer=self.sparse_tk,
                similarity_top_k=f_topk_3,
                stopwords=self.stp_words,
                embed_type=5,  # 4-->file_path 5-->know_path
                bm25_type=bm25_type,
            )
        else:
            self.path_retriever = None

        if split_type == 1:
            self.sparse_retriever = AutoMergingRetriever(
                self.sparse_retriever,
                storage_context,
                simple_ratio_thresh=0.4,
            )
        print("创建BM25稀疏检索器成功")

        # 创建node快速索引
        self.nodeid2idx = dict()
        for i, node in enumerate(self.nodes):
            self.nodeid2idx[node.node_id] = i

        self.retriever = self.dense_retriever

        # 创建重排器
        self.reranker = None
        use_reranker = config['use_reranker']
        r_topk = config['r_topk']
        reranker_name = config['reranker_name']
        r_embed_type = config['r_embed_type']
        r_embed_bs = config['r_embed_bs']
        r_use_efficient = config['r_use_efficient']

        self.local_llm_name = config.get('local_llm_name', "")

        compress_method = config['compress_method']
        compress_rate = config['compress_rate']
        self.compressor = None
        print("EasyRAGPipeline 初始化完成".center(60, "="))

    def build_prompt_template(self, qa_template):
        return PromptTemplate(qa_template)

    def build_filters(self, query):
        filters = None
        filter_dict = None
        if "document" in query and query["document"] != "":
            dir = query['document']
            filters = build_qdrant_filters(
                dir=dir
            )
            filter_dict = {
                "dir": dir
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
            query_str=query["query"],
            hyde_query=query.get("hyde_query", "")
        )
        return res

    async def generation_with_knowledge_retrieval(
            self,
            query_str: str,
            hyde_query: str = ""
    ):
        query_bundle = self.build_query_bundle(query_str + hyde_query)
        node_with_scores = await self.sparse_retriever.aretrieve(query_bundle)
        if self.path_retriever is not None:
            node_with_scores_path = await self.path_retriever.aretrieve(query_bundle)
        else:
            node_with_scores_path = []
        node_with_scores = HybridRetriever.fusion([
            node_with_scores,
            node_with_scores_path,
        ])

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
        return {"answer": ret.text, "nodes": node_with_scores, "contexts": contents}
