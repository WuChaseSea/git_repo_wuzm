import os
from pathlib import Path
from typing import List, Union

from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from llama_index.core import QueryBundle
from llama_index.core.embeddings import BaseEmbedding
from llama_index.embeddings.langchain import LangchainEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.vector_stores.types import BasePydanticVectorStore
from llama_index.core.node_parser.text.sentence import SentenceSplitter
from llama_index.readers.file import PDFReader
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.schema import Document, TransformComponent

from qdrant_client import QdrantClient, models
from qdrant_client.http.exceptions import UnexpectedResponse

import settings
from settings import VP_APP_DATA_DIR
from apps.pipelines.retrievers import QdrantRetriever

class FilePipeline():

    def __init__(
            self,
            filepath
            ):
        model_name = settings.EMBEDDING_MODEL
        model_kwargs = {'device': 'cpu'}
        encode_kwargs = {'normalize_embeddings': False}
        bge_embeddings = HuggingFaceBgeEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )
        embedding = LangchainEmbedding(bge_embeddings)
        print(f"embedding model build succeed.")
        chunk_size, chunk_overlap = 300, 50
        cache_path = str(Path(VP_APP_DATA_DIR) / "vectorstore")
        collection_name = Path(filepath).name
        client, vector_store = self.build_vector_store(
            cache_path=cache_path,
            reindex=False,
            collection_name=collection_name,
            vector_size=settings.EMBEDDING_VECTOR_SIZE
        )
        reader = PDFReader()
        data = reader.load_data(file=filepath)
        print(f'read pdf data succeed.')
        collection_info = client.get_collection(collection_name=Path(filepath).name)
        pipeline = self.build_pipeline(
            embedding, vector_store, filepath, chunk_size, chunk_overlap
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
            
            pipeline.persist(os.path.join(cache_path, f"pipeline_storage_{collection_name}"))

            print(f"索引建立完成，一共有{len(nodes)}个节点")
        else:
            pipeline.load(os.path.join(cache_path, f"pipeline_storage_{collection_name}"))
            nodes = pipeline.run(documents=data, show_progress=True, num_workers=1)
        
        self.dense_retriever = QdrantRetriever(vector_store, embedding, similarity_top_k=8)

    
    def build_vector_store(
            self,
            cache_path,
            reindex,
            collection_name,
            vector_size
    ) -> tuple[QdrantClient, QdrantVectorStore]:
        client = QdrantClient(
            path=cache_path
        )
        if reindex:
            try:
                client.delete_collection(collection_name)
            except UnexpectedResponse as e:
                print(f"Collection not found: {e}")
        try:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size, distance=models.Distance.COSINE
                ),
            )
        except Exception as e:
            print("集合已存在")
        return client, QdrantVectorStore(
            client=client,
            collection_name=collection_name
        )
    
    def build_preprocess(self,
        data_path=None,
        chunk_size=1024,
        chunk_overlap=50
    ) -> List[TransformComponent]:
        parser = SentenceSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            include_prev_next_rel=True,
        )
        transformation = [
            parser
        ]
        return transformation
    
    def build_pipeline(self,
        embed_model: BaseEmbedding,
        vector_store: BasePydanticVectorStore = None,
        data_path=None,
        chunk_size=1024,
        chunk_overlap=50,
    ) -> IngestionPipeline:
        transformation = self.build_preprocess(
            data_path,
            chunk_size,
            chunk_overlap,
        )
        transformation.extend([
            embed_model,
        ])
        return IngestionPipeline(transformations=transformation, vector_store=vector_store)
    
    def build_query_bundle(self, query_str):
        query_bundle = QueryBundle(query_str=query_str)
        return query_bundle
    
    def retrieve(self, query_str):
        query_bundle = self.build_query_bundle(query_str)
        node_with_scores = self.dense_retriever.retrieve(query_bundle)
        return node_with_scores


if __name__ == "__main__":
    pass
