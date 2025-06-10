# EasyRAG reproduce

## 基本流程：

构建LLM

本研究通过阿里百炼大模型平台调用qwen-max api接口；

构建Embedding

使用bge-small-zh-v1.5获取embedding

读取文档信息
基于LLAMA-Index提供的SimpleDirectoryReader直接读取文件夹中的所有txt文件；

向量入库，使用Qdrant数据库将之前的embedding信息存入数据库，建立索引。

构建检索器
直接采用QdrantRetriever构建密集检索，选择最相似的前64个片段

## 结果比较

基础版本：

使用密集索引，在验证集上关键词精度0.55

使用稀疏索引，在验证集上关键词精度0.54

