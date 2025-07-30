import os
from langchain_community.llms import OpenAI
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.chains import LLMChain, HypotheticalDocumentEmbedder
from langchain.prompts import PromptTemplate
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.chat_models.tongyi import ChatTongyi


model_name = r"E:\Models\embedding\bge-m3"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}
bge_embeddings = HuggingFaceBgeEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

llm = ChatTongyi(model='qwen-plus', temperature=1.0)

# 使用`web_search`提示加载
embeddings = HypotheticalDocumentEmbedder.from_llm(llm, bge_embeddings, "web_search")

prompt_template = """请回答用户关于最近一次国情咨文的问题
问题：{question}
答案："""
prompt = PromptTemplate(input_variables=["question"], template=prompt_template)
llm_chain = LLMChain(llm=llm, prompt=prompt)

from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma

with open("../../data/state_of_the_union.txt", encoding="utf-8") as f:
    state_of_the_union = f.read()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_text(state_of_the_union)

docsearch = Chroma.from_texts(texts, embeddings)

query = "总统对Ketanji Brown Jackson有什么说法？"
docs = docsearch.similarity_search(query)

print(docs[0].page_content)
