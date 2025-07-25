from pathlib import Path
from llama_index.readers.file import PDFReader
from llama_index.core.response.notebook_utils import display_source_node
from llama_index.core.retrievers import RecursiveRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core import VectorStoreIndex
from llama_index.llms.openai import OpenAI
import json

loader = PDFReader()
docs0 = loader.load_data(file=Path("./data/llama2.pdf"))
from llama_index.core import Document

doc_text = "\n\n".join([d.get_content() for d in docs0])
docs = [Document(text=doc_text)]
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import IndexNode

node_parser = SentenceSplitter(chunk_size=1024)

base_nodes = node_parser.get_nodes_from_documents(docs)
# set node ids to be a constant
for idx, node in enumerate(base_nodes):
    node.id_ = f"node-{idx}"
from llama_index.core.embeddings import resolve_embed_model

embed_model = resolve_embed_model("local:/Users/wuzm/Documents/CodeRepository/Models/embedding_models/bge-small-en-v1.5")
base_index = VectorStoreIndex(base_nodes, embed_model=embed_model)
# base_retriever = base_index.as_retriever(similarity_top_k=2)

sub_chunk_sizes = [128, 256, 512]
sub_node_parsers = [
    SentenceSplitter(chunk_size=c, chunk_overlap=20) for c in sub_chunk_sizes
]

all_nodes = []
for base_node in base_nodes:
    for n in sub_node_parsers:
        sub_nodes = n.get_nodes_from_documents([base_node])
        sub_inodes = [
            IndexNode.from_text_node(sn, base_node.node_id) for sn in sub_nodes
        ]
        all_nodes.extend(sub_inodes)

    # also add original node to node
    original_node = IndexNode.from_text_node(base_node, base_node.node_id)
    all_nodes.append(original_node)

all_nodes_dict = {n.node_id: n for n in all_nodes}
vector_index_chunk = VectorStoreIndex(all_nodes, embed_model=embed_model)
vector_retriever_chunk = vector_index_chunk.as_retriever(similarity_top_k=10)
retriever_chunk = RecursiveRetriever(
    "vector",
    retriever_dict={"vector": vector_retriever_chunk},
    node_dict=all_nodes_dict,
    verbose=True,
)
nodes = vector_retriever_chunk.retrieve("Can you tell me about the key concepts for safety finetuning")
for node in nodes:
    print(node.score, node.node_id)
    print(node.get_content())
    print("-" * 80)
# nodes = retriever_chunk.retrieve(
#     "Can you tell me about the key concepts for safety finetuning"
# )
# for node in nodes:
#     print(node)

