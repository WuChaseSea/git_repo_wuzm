### Build Index
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceBgeEmbeddings

# Set embeddings
# embd = CohereEmbeddings()
# model_name = r"E:\Models\embedding\bge-m3"
model_name = "/Users/wuzm/Documents/CodeRepository/Models/embedding_models/bge-m3"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}
embd = HuggingFaceBgeEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

# Docs to index
urls = [
    "https://lilianweng.github.io/posts/2023-06-23-agent/",
    "https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/",
    "https://lilianweng.github.io/posts/2023-10-25-adv-attack-llm/",
]

# Add to vectorstore
persist_directory = "db"
if Path(persist_directory).exists():
    vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embd)
else:
    # Load
    docs = [WebBaseLoader(url).load() for url in urls]
    docs_list = [item for sublist in docs for item in sublist]

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

### Router
from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_community.chat_models.tongyi import ChatTongyi

# Data model
class web_search(BaseModel):
    """
    The internet. Use web_search for questions that are related to anything else than agents, prompt engineering, and adversarial attacks.
    """
    query: str = Field(description="The query to use when searching the internet.")

class vectorstore(BaseModel):
    """
    A vectorstore containing documents related to agents, prompt engineering, and adversarial attacks. Use the vectorstore for questions on these topics.
    """
    query: str = Field(description="The query to use when searching the vectorstore.")

# Preamble
preamble = """You are an expert at routing a user question to a vectorstore or web search.
The vectorstore contains documents related to agents, prompt engineering, and adversarial attacks.
Use the vectorstore for questions on these topics. Otherwise, use web-search."""

# LLM with tool use and preamble
llm = ChatTongyi(model='qwen-plus', temperature=0.0)
structured_llm_router = llm.bind_tools(tools=[web_search, vectorstore], preamble=preamble)

# Prompt
route_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{question}"),
    ]
)

# question_router = route_prompt | structured_llm_router
# response = question_router.invoke({"question": "Who will the Bears draft first in the NFL draft?"})
# print(response.tool_calls)
# response = question_router.invoke({"question": "What are the types of agent memory?"})
# print(f"1111")
# print(response.tool_calls)
# response = question_router.invoke({"question": "Hi how are you?"})
# print("******")
# print(response.tool_calls)

### Retrieval Grader

# Data model
class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""

    binary_score: str = Field(description="Documents are relevant to the question, 'yes' or 'no'")

# Prompt
preamble = """You are a grader assessing relevance of a retrieved document to a user question. \n
If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n
Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."""


# structured_llm_grader = llm.with_structured_output(GradeDocuments)

# grade_prompt = ChatPromptTemplate.from_messages(
#     [
#         ("system", preamble),
#         ("human", "Retrieved document: \n\n {document} \n\n User question: {question}"),
#     ]
# )

# retrieval_grader = grade_prompt | structured_llm_grader
question = "types of agent memory"
docs = retriever.invoke(question)
# doc_txt = docs[1].page_content
# response =  retrieval_grader.invoke({"question": question, "document": doc_txt})
# print(response)

### Generate

from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage


# Preamble
preamble = """You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise."""

# Prompt
prompt = lambda x: ChatPromptTemplate.from_messages(
    [
        HumanMessage(
            f"Question: {x['question']} \nAnswer: ",
            additional_kwargs={"documents": x["documents"]},
        )
    ]
)

# Chain
rag_chain = prompt | llm | StrOutputParser()

# Run
generation = rag_chain.invoke({"documents": docs, "question": question})
print(generation)
