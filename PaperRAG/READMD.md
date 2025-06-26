# PaperRAG

实验记录

baseline
chunk 1024 overlap 50
bge-base-zh-v1.5 密集检索 top32 0.3956  (qwen-max)
**bge-base-en-v1.5 密集检索 top32 0.4311  (qwen-max-2025-01-25)**
bge-base-en-v1.5 密集检索 top8 0.4000 (qwen-plus)
bge-base-en-v1.5 bm25检索 top8 0.4044 (qwen-plus-1125)

bge-base-en-v1.5 密集检索 top32 bge-reranker-v2-m3 rerank top6 0.3689 (qwen-plus-1220)
bge-base-en-v1.5 bm25检索 top8 bge-reranker-v2-m3 rerank top6 0.3956 (qwen-plus-1127)
bge-base-en-v1.5 bm25检索 top16 bge-reranker-v2-m3 rerank top6 0.3644 (qwen-plus-0112)
bge-base-en-v1.5 bm25检索 top32 bge-reranker-v2-m3 rerank top6 0.3733 (qwen-plus-1220)
bge-base-en-v1.5 bm25检索 top32 bge-reranker-v2-minicpm-layerwise rerank top6 0.3733 (qwen-plus-0112)

chunk 512 overlap 128
**bge-base-en-v1.5 bm25检索 top8 0.4356 (qwen-plus-2025-01-25)**
bge-base-en-v1.5 bm25检索 top16 0.4222 (qwen-plus-latest)
bge-base-en-v1.5 密集检索 top32 0.3733 (qwen-plus-latest)
bge-base-en-v1.5 密集检索 top32 0.3644  (qwen-max-2025-01-25) ？？？
bge-base-en-v1.5 bm25检索 top8 0.3733 (qwen-plus-latest)  这个地方很奇怪，为什么一样的配置效果变差了，难道是LLM的问题
bge-base-en-v1.5 bm25检索 top16 bge-reranker-v2-m3 rerank top8 0.4267 (qwen-plus-latest)
bge-base-en-v1.5 bm25检索 从query、A、B、C、D四个选项中分别进行召回top8，然后进行合并，rerank top8 0.3778 (qwen-plus-latest)
bge-base-en-v1.5 bm25检索 从query、A、B、C、D四个选项中分别进行召回top2，然后进行合并 0.3956 (qwen-plus-latest)
bge-base-en-v1.5 密集检索 top8 0.4000 (qwen-plus-latest)
bge-base-en-v1.5 bm25检索 top32 bge-reranker-v2-m3 rerank top6 0.4089 (qwen-plus-2025-01-25)
bge-base-en-v1.5 bm25检索 top8 密集检索 top8 混合检索 top8 bge-reranker-v2-m3 rerank top6 0.4178 (qwen-plus-2025-04-28)
bge-base-en-v1.5 bm25检索 top8 密集检索 top8 混合检索 top8 0.3911 (qwen-plus-2025-04-28)
bge-base-en-v1.5 hierarchical 密集检索 top8 0.4089 (qwen-plus-latest)
bge-base-en-v1.5 hierarchical 密集检索 top8 0.3644 en-template (qwen-plus-latest)

bge-base-en-v1.5 bm25检索 top8 0.4044 (qwen-plus-2025-01-25)
bge-base-en-v1.5 bm25检索 top8 0.4089 (qwen-plus-2025-01-25) 重新embedding
bge-base-en-v1.5 bm25检索 top8 0.3911 (qwen-plus-2025-01-25) 固定temperature
bge-base-en-v1.5 bm25检索 top8 0.3867 (qwen-plus-latest)
bge-base-en-v1.5 bm25检索 top8 0.3911 (qwen-plus-2025-01-25)
bge-base-en-v1.5 bm25检索 top8 0.3244 (qwen-max)
bge-base-en-v1.5 bm25检索 top16 0.3867 (qwen-plus-latest)
回退0617 bge-base-en-v1.5 密集检索 top8 0.3956 (qwen-plus-latest)
回退0617 bge-base-en-v1.5 bm25检索 top8 0.3822 (qwen-plus-latest)
回退更早0614 bge-base-en-v1.5 bm25检索 top8 0.4267 (qwen-plus-latest)

chunk 300 overlap 50
bge-base-en-v1.5 密集检索 top8 0.3778 (qwen-plus-latest)
bge-base-en-v1.5 密集检索 top32 0.4000 (qwen-plus-latest) 添加rerank，使用LLM分数评判，仅提交前30个 0.0622
bge-base-en-v1.5 bm25 top8 0.3822 (qwen-plus-latest)
bge-base-en-v1.5 bm25 top32 0.3778 (qwen-plus-latest)  仅提交前30个 0.08

chunk 512 overlap 128
bge-base-en-v1.5 bm25 top8 0.3733 (qwen-plus-latest)

使用pdfplumber
bge-base-en-v1.5 bm25检索 top8 密集检索 top8 混合检索 top8 0.3822 (qwen-plus-2025-04-28) base_version_1.json
bge-base-en-v1.5 bm25检索 top8  0.3556 (qwen-plus-2025-04-28) base_version_2.json

使用PyMuPDF（fitz）
bge-base-en-v1.5 bm25检索 top8 0.3244 qwen/qwen2.5-7b-instruct
bge-base-en-v1.5 bm25检索 top8 0.3733 (qwen-plus-latest) base_version_0617_1 base_version_0617_1

使用pypdf
bge-base-en-v1.5 bm25检索 top8 0.3467 deepseek/deepseek-r1-distill-qwen-32b

使用UnstructuredPDFLoader
bge-base-en-v1.5 hierarchical 密集检索 top8 0.3378 (qwen-plus-latest)

VL实验
colpali-v1.2 top8 qwen-vl-plus 0.3156
colpali-v1.2 top8 qwen-vl-max-latest 0.3733

debug思路：
添加保存node节点到csv中，以便查看node是否✅；
使用之前的embedding和重新embedding之后看看查找的是否对；

试了：
chunk500 overlap 128
密集top32 top32 0.3644
密集 top8 用之前的embedding 0.3778

chunk300 overlap 50
密集 top32 0.3733
bm25 top8 0.3689

尝试：已经将reader退回之前的代码了，明天再跑一遍重新生成512的embedding，bm25检索；
