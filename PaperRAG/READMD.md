# PaperRAG

实验记录

baseline

bge-base-zh-v1.5 密集检索 top32 0.3956  (qwen-max)
bge-base-en-v1.5 密集检索 top32 0.4311  (qwen-max-2025-01-25)
bge-base-en-v1.5 密集检索 top8 0.4000 (qwen-plus)
bge-base-en-v1.5 bm25检索 top8 0.4044 (qwen-plus-1125)
bge-base-en-v1.5 bm25检索 top8 bge-reranker-v2-m3 rerank top6 0.3956 (qwen-plus-1127)

bge-base-en-v1.5 密集检索 top32 bge-reranker-v2-m3 rerank top6
bge-base-en-v1.5 bm25检索 top32 bge-reranker-v2-m3 rerank top6
bge-base-en-v1.5 bm25检索 top32 bge-reranker-v2-m3 rerank top6

