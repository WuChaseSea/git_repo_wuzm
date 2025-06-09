# -*-coding:UTF-8 -*-
"""
* main.py
* @author wuzm
* created 2025/06/06 16:28:45
* @function: 主程序入口
"""
import os
import json
import fire
from tqdm.asyncio import tqdm

from src.easyrag.utils import get_yaml_data
from src.easyrag.pipeline import EasyRAGPipeline, read_jsonl


def get_test_data(split="val"):
    if split == "test":
        queries = read_jsonl("/Users/wuzm/Documents/CodeRepository/git_repo_wuzm/EasyRAG/src/data/question.jsonl")
    else:
        with open("/Users/wuzm/Documents/CodeRepository/git_repo_wuzm/EasyRAG/src/data/val.json") as f:
            queries = json.loads(f.read())
    return queries


async def main(
        split="val",
        config_path="src/configs/easyrag.yaml"
):
    config = get_yaml_data(config_path)
    for key in config:
        print(f"{key}: {config[key]}")

    rag_pipeline = EasyRAGPipeline(
        config
    )

    queries = get_test_data(split)
    print(f"开始生成答案...")
    answers = []
    all_nodes = []
    all_contexts = []
    all_keyword_acc = 0
    N = len(queries)
    for num, query in enumerate(tqdm(queries, total=len(queries))):
        res = await rag_pipeline.run(query)

        answer = res["answer"]
        keywords = query["keywords"]
        M = len(keywords)
        keyword_acc = 0
        for keyword in keywords:
            if keyword in answer:
                keyword_acc += 1
        keyword_acc /= M
        all_keyword_acc += keyword_acc
        print(f"query {num} acc: {keyword_acc}")
    all_keyword_acc /= N
    print(f"queries average acc: {all_keyword_acc}")


if __name__ == "__main__":
    fire.Fire(main)
