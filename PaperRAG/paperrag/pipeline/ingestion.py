# -*-coding:UTF-8 -*-
'''
* injection.py
* @author wuzm
* created 2025/06/11 19:18:03
* @function: 
'''
import os
import json
import pickle
from typing import List, Union
from pathlib import Path
from tqdm import tqdm

from dotenv import load_dotenv
from openai import OpenAI
from rank_bm25 import BM25Okapi
import faiss
import numpy as np
from tenacity import retry, wait_fixed, stop_after_attempt

from typing import List
# from llama_index.core import SimpleDirectoryReader
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.llms.llm import LLM
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.vector_stores.types import BasePydanticVectorStore
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import Document, TransformComponent, NodeWithScore, TextNode, NodeRelationship
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient, models
from qdrant_client.http.exceptions import UnexpectedResponse

from qdrant_client.http.models import Filter, FieldCondition, MatchValue

from ..custom.reader import SimpleDirectoryReader
from ..custom.hierarchical import HierarchicalNodeParser


def read_data(path: str = "data") -> List[Document]:
    reader = SimpleDirectoryReader(
        input_dir=path,
        recursive=True,
        required_exts=[
            ".pdf"
        ],
        encoding="utf-8"
    )
    return reader.load_data()


def merge_strings(A, B):
    # 找到A的结尾和B的开头最长的匹配子串
    max_overlap = 0
    min_length = min(len(A), len(B))

    for i in range(1, min_length + 1):
        if A[-i:] == B[:i]:
            max_overlap = i

    # 合并A和B，去除重复部分
    merged_string = A + B[max_overlap:]
    return merged_string


def get_node_content(node: NodeWithScore, embed_type=0, nodes: list[TextNode] = None, nodeid2idx: dict = None) -> str:
    text: str = node.get_content()
    if embed_type == 6:
        cur_text = text
        if cur_text.count("|") >= 5 and cur_text.count("---") == 0:
            cnt = 0
            flag = False
            while True:
                pre_node_id = node.node.relationships[NodeRelationship.PREVIOUS].node_id
                pre_node = nodes[nodeid2idx[pre_node_id]]
                pre_text = pre_node.text
                cur_text = merge_strings(pre_text, cur_text)
                cnt += 1
                if pre_text.count("---") >= 2:
                    flag = True
                    break
                if cnt >= 3:
                    break
            if flag:
                idx = cur_text.index("---")
                text = cur_text[:idx].strip().split("\n")[-1] + cur_text[idx:]
            # print(flag, cnt)
    if embed_type == 1:
        if 'file_path' in node.metadata:
            text = '###\n' + node.metadata['file_path'] + "\n\n" + text
    elif embed_type == 2:
        if 'know_path' in node.metadata:
            text = '###\n' + node.metadata['know_path'] + "\n\n" + text
    elif embed_type == 3 or embed_type == 6:
        if "imgobjs" in node.metadata and len(node.metadata['imgobjs']) > 0:
            for imgobj in node.metadata['imgobjs']:
                text = text.replace(f"{imgobj['cap']} {imgobj['title']}\n",
                                    f"{imgobj['cap']}.{imgobj['title']}:{imgobj['content']}\n")
    elif embed_type == 4:
        if 'file_path' in node.metadata:
            text = node.metadata['file_path']
        else:
            text = ""
    elif embed_type == 5:
        if 'know_path' in node.metadata:
            text = node.metadata['know_path']
        else:
            text = ""
    return text


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
        # CustomTitleExtractor(metadata_mode=MetadataMode.EMBED),
        # CustomFilePathExtractor(last_path_length=100000, data_path=data_path, metadata_mode=MetadataMode.EMBED),
    ]
    return transformation


def build_vector_store(
        qdrant_url: str = "http://localhost:6333",
        cache_path: str = "cache",
        reindex: bool = False,
        collection_name: str = "aiops24",
        vector_size: int = 3584,
) -> tuple[QdrantClient, QdrantVectorStore]:
    client = QdrantClient(
        path=cache_path,
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


def build_qdrant_filters(dir):
    filters = Filter(
        must=[
            FieldCondition(
                key="dir",
                match=MatchValue(value=dir),
            )
        ]
    )
    return filters

class BM25Ingestor:
    def __init__(self):
        pass

    def create_bm25_index(self, chunks: List[str]) -> BM25Okapi:
        """Create a BM25 index from a list of text chunks."""
        tokenized_chunks = [chunk.split() for chunk in chunks]
        return BM25Okapi(tokenized_chunks)
    
    def process_reports(self, all_reports_dir: Path, output_dir: Path):
        """Process all reports and save individual BM25 indices.
        
        Args:
            all_reports_dir (Path): Directory containing the JSON report files
            output_dir (Path): Directory where to save the BM25 indices
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        all_report_paths = [f for f in all_reports_dir.rglob("*.json") if not f.name.startswith("._")]

        for report_path in tqdm(all_report_paths, desc="Processing reports for BM25"):
            # Load the report
            with open(report_path, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
                
            # Extract text chunks and create BM25 index
            text_chunks = [chunk['text'] for chunk in report_data['content']['chunks']]
            bm25_index = self.create_bm25_index(text_chunks)
            
            # Save BM25 index
            sha1_name = report_data["metainfo"]["sha1_name"]
            output_file = output_dir / f"{sha1_name}.pkl"
            with open(output_file, 'wb') as f:
                pickle.dump(bm25_index, f)
                
        print(f"Processed {len(all_report_paths)} reports")

class VectorDBIngestor:
    def __init__(self, embedding_model):
        # self.llm = self._set_up_llm()
        self.llm = None
        self.embedding_model = embedding_model

    def _set_up_llm(self):
        load_dotenv()
        llm = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            timeout=None,
            max_retries=2
        )
        return llm

    @retry(wait=wait_fixed(20), stop=stop_after_attempt(2))
    def _get_embeddings(self, text: Union[str, List[str]], model: str = "text-embedding-3-large") -> List[float]:
        if isinstance(text, str) and not text.strip():
            raise ValueError("Input text cannot be an empty string.")
        
        if isinstance(text, list):
            text_chunks = [text[i:i + 1024] for i in range(0, len(text), 1024)]
        else:
            text_chunks = [text]

        embeddings = []
        for chunk in text_chunks:
            # import ipdb;ipdb.set_trace()
            # response = self.llm.embeddings.create(input=chunk, model=model)
            # response = self.embedding_model.embed_query(chunk)
            for chunk_one in chunk:
                response = self.embedding_model.embed_query(chunk_one)
                embeddings.extend([response])
            # embeddings.extend([embedding.embedding for embedding in response.data])
        
        return embeddings

    def _create_vector_db(self, embeddings: List[float]):
        embeddings_array = np.array(embeddings, dtype=np.float32)
        dimension = len(embeddings[0])
        index = faiss.IndexFlatIP(dimension)  # Cosine distance
        index.add(embeddings_array)
        return index
    
    def _process_report(self, report: dict):
        text_chunks = [chunk['text'] for chunk in report['content']['chunks']]
        embeddings = self._get_embeddings(text_chunks)
        index = self._create_vector_db(embeddings)
        return index

    def process_reports(self, all_reports_dir: Path, output_dir: Path):
        all_report_paths = list(all_reports_dir.glob("*.json"))
        output_dir.mkdir(parents=True, exist_ok=True)

        for report_path in tqdm(all_report_paths, desc="Processing reports"):
            with open(report_path, 'r', encoding='utf-8') as file:
                report_data = json.load(file)
            index = self._process_report(report_data)
            sha1_name = report_data["metainfo"]["sha1_name"]
            faiss_file_path = output_dir / f"{sha1_name}.faiss"
            faiss.write_index(index, str(faiss_file_path))

        print(f"Processed {len(all_report_paths)} reports")
