# -*-coding:UTF-8 -*-
'''
* main.py
* @author wuzm
* created 2025/06/11 14:25:18
* @function: 
'''
import os
import fire
import re
import json
from tqdm.asyncio import tqdm
from copy import deepcopy

from paperrag.utils import get_yaml_data, read_jsonl
from paperrag.pipeline import PaperRAGPipeline

def change_result(raw_text):
    # 提取 JSON 字符串部分（用正则找出最外层花括号里的部分）
    try:
        match = re.search(r'{[\s\S]*?}', raw_text)
        if match:
            json_str = match.group(0)
            # 将 True/False 替换为 JSON 兼容格式 true/false
            json_str = json_str.replace('True', 'true').replace('False', 'false')
            # 加载为字典
            data = json.loads(json_str)
            # 选出为 True 的 key 并拼接
            result = ''.join([k for k, v in data.items() if v])
            return result
        else:
            print("未找到 JSON 格式的数据")
            return None
    except Exception as e:
        print(f"字符串: {raw_text} 出现错误: {e}")
        return None


async def main(
        split="val",
        config_path="configs/paperrag.yaml"
):
    config = get_yaml_data(config_path)
    for key in config:
        print(f"{key}: {config[key]}")
    
    rag_pipeline = PaperRAGPipeline(
        config
    )

    question_file = "E:/Dataset/TIANCHIPaperRAG/papar_QA_dataset/multi_choice_questions.json"
    with open(question_file, encoding="utf-8") as f:
        queries = json.loads(f.read())
    print(f"开始生成答案...")
    results = deepcopy(queries)
    for num, query in enumerate(tqdm(queries, total=len(queries))):
        res = await rag_pipeline.run(query)
        answer = res["answer"]
        answer = change_result(answer)
        if answer is None:
            print(f"id {num}: 输出结果不对".center(60, "*"))
        else:
            print(f"id {num}: {answer}")
        results[num]["correct_answer"] = answer
    save_json = "base_version.json"
    with open(save_json, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    

if __name__ == "__main__":
    fire.Fire(main)