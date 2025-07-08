from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.chat_models.tongyi import ChatTongyi

# 构建embedding模型
# model_name = r"E:\Models\embedding\bge-m3"
model_name = "/Users/wuzm/Documents/CodeRepository/Models/embedding_models/bge-m3"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}
embd = HuggingFaceBgeEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

# 构建文献索引
urls = [
    "https://lilianweng.github.io/posts/2023-06-23-agent/",
    "https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/",
    "https://lilianweng.github.io/posts/2023-10-25-adv-attack-llm/",
]

# Add to vectorstore
persist_directory = "db"
docs = [WebBaseLoader(url).load() for url in urls]
docs_list = [item for sublist in docs for item in sublist]

if Path(persist_directory).exists():
    vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embd)
else:
    
    # Split
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=512, chunk_overlap=0
    )
    doc_splits = text_splitter.split_documents(docs_list)
    vectorstore = Chroma.from_documents(
        documents=doc_splits,
        embedding=embd,
        persist_directory=persist_directory
    )
    # 持久化数据，并释放内存
    vectorstore.persist()
    vectorstore = None
    vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embd)

retriever = vectorstore.as_retriever()

llm = ChatTongyi(model='qwen-plus', temperature=0.0)
