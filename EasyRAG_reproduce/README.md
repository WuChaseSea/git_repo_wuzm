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

## 提供结果分析

单路径粗排

bge-small-zh-v1.5 top3 57
bge-base-zh-v1.5 top8 68
bm25文本块检索 top8 69

重排

bge-base top192 bge-reranker-v2-m3 top8 73
bge-base top256 bge-reranker-v2-m3 top8 70
bce-embedding-base_v1 top192 bce-reranker-base_v1 top8 69

基于LLM-Reranker的重排

bge-base top288 40层的bge-reranker-v2-minicpm-layerwise top8 77

## 结果比较

基础版本：

chunk size 1024 overlap 200 top48 使用密集索引，在验证集上关键词精度0.55

chunk size 1024 overlap 200 top32 使用稀疏索引，在验证集上关键词精度0.54

chunk size 1024 overlap 50 top3 使用密集索引，在验证集上关键词精度0.29
chunk size 1024 overlap 50 top48 使用密集索引，在验证集上关键词精度0.54
chunk size 1024 overlap 50 top8 使用密集索引，在验证集上关键词精度0.42
bge-base
chunk size 1024 overlap 50 top48 使用密集索引，在验证集上关键词精度0.52
chunk size 1024 overlap 50 top32 使用密集索引，在验证集上关键词精度0.49
