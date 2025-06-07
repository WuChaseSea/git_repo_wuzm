from typing import List
from llama_index.core import SimpleDirectoryReader
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.schema import Document, TransformComponent, MetadataMode
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.llms.llm import LLM
from llama_index.core.vector_stores.types import BasePydanticVectorStore
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import AsyncQdrantClient, models
from qdrant_client.http.exceptions import UnexpectedResponse

from ..custom import SentenceSplitter, HierarchicalNodeParser, CustomTitleExtractor, CustomFilePathExtractor


def read_data(path: str = "data") -> List[Document]:
    reader = SimpleDirectoryReader(
        input_dir=path,
        recursive=True,
        required_exts=[
            ".txt"
        ],
    )
    return reader.load_data()


def build_preprocess(
        data_path=None,
        chunk_size=1024,
        chunk_overlap=50,
        split_type=0,  # 0-->Sentence 1-->Hierarchical
) -> List[TransformComponent]:
    if split_type == 0:
        parser = SentenceSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            include_prev_next_rel=True,
        )
    else:
        parser = HierarchicalNodeParser.from_defaults(
            chunk_sizes=[chunk_size * 4, chunk_size],
            chunk_overlap=chunk_overlap,
        )
    transformation = [
        parser,
        CustomTitleExtractor(metadata_mode=MetadataMode.EMBED),
        CustomFilePathExtractor(last_path_length=100000, data_path=data_path, metadata_mode=MetadataMode.EMBED),
    ]
    return transformation


def build_preprocess_pipeline(
        data_path=None,
        chunk_size=1024,
        chunk_overlap=50,
        split_type=0,
) -> IngestionPipeline:
    transformation = build_preprocess(
        data_path,
        chunk_size,
        chunk_overlap,
        split_type=split_type,
    )
    return IngestionPipeline(transformations=transformation)


async def build_vector_store(
        qdrant_url: str = "http://localhost:6333",
        cache_path: str = "cache",
        reindex: bool = False,
        collection_name: str = "aiops24",
        vector_size: int = 3584,
) -> tuple[AsyncQdrantClient, QdrantVectorStore]:
    # if qdrant_url:
    #     client = AsyncQdrantClient(
    #         url=qdrant_url,
    #     )
    # else:
    #     client = AsyncQdrantClient(
    #         path=cache_path,
    #     )
    client = AsyncQdrantClient(
        path=cache_path,
    )

    if reindex:
        try:
            await client.delete_collection(collection_name)
        except UnexpectedResponse as e:
            print(f"Collection not found: {e}")

    try:
        await client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=vector_size, distance=models.Distance.COSINE
            ),
        )
    except Exception as e:
        print("集合已存在")
    return client, QdrantVectorStore(
        aclient=client,
        collection_name=collection_name,
        parallel=4,
        batch_size=32,
    )


def build_pipeline(
        llm: LLM,
        embed_model: BaseEmbedding,
        template: str = None,
        vector_store: BasePydanticVectorStore = None,
        data_path=None,
        chunk_size=1024,
        chunk_overlap=50,
) -> IngestionPipeline:
    transformation = build_preprocess(
        data_path,
        chunk_size,
        chunk_overlap,
    )
    transformation.extend([
        # SummaryExtractor(
        #     llm=llm,
        #     metadata_mode=MetadataMode.EMBED,
        #     prompt_template=template or SUMMARY_EXTRACT_TEMPLATE,
        # ),
        embed_model,
    ])
    return IngestionPipeline(transformations=transformation, vector_store=vector_store)
