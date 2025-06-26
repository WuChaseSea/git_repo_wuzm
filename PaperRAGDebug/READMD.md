# PaperRAG

config/paperrag.yaml里面修改属性值：

```yaml
work_dir: "/Volumes/Dataset/TIANCHIPaperRAG"  # 项目目录
embedding_name: "/Users/Documents/Models/embedding_models/bge-base-en-v1.5"  # bge-base-en-v1.5路径位置
reranker_name: "/Users/Documents/Models/reranker/bge-reranker-v2-m3"  # bge-reranker-v2-m3路径位置
```

运行方式

```python
python main.py
```
