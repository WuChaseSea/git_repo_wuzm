# -*-coding:UTF-8 -*-
'''
* main.py
* @author wuzm
* created 2025/06/11 14:25:18
* @function: 
'''
import os, sys
from pathlib import Path
import fire
import re
import json
from tqdm.asyncio import tqdm
from copy import deepcopy
from datetime import datetime
import pandas as pd

from paperrag.utils import get_yaml_data, read_jsonl
from paperrag.pipeline import PaperRAGPipeline
from paperrag.pipeline import PaperRAGChallengePipeline


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

    # rag_pipeline = PaperRAGChallengePipeline(
    #     config
    # )
    rag_pipeline = PaperRAGPipeline(
        config
    )

    question_file = str(Path(config["work_dir"]) / "papar_QA_dataset/multi_choice_questions_class.json")
    with open(question_file, encoding="utf-8") as f:
        queries = json.loads(f.read())
    print(f"开始生成答案...")
    results = deepcopy(queries)
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # save_folder = Path(config["work_dir"]) / f"result_{current_time}"
    save_folder = Path(config["work_dir"]) / config["result_dir"]
    
    # save_folder = Path(config["work_dir"]) / f"result_2025-06-23_21-21-45"
    save_folder.mkdir(parents=True, exist_ok=True)

    papers_id_list, querys_list = [], []
    nodes_list, scores_list, answer_list = [], [], []
    all_rows = []
    for num, query in enumerate(tqdm(queries, total=len(queries))):
        # if num < 223:
        #     save_one_json = save_folder / f"{num}.json"
        #     with open(save_one_json, encoding="utf-8") as f:
        #         answer = json.loads(f.read())
        #     results[num]["correct_answer"] = answer['correct_answer']
        #     continue
        # import ipdb;ipdb.set_trace()
        res = await rag_pipeline.run(query)
        # res = await rag_pipeline.process_quesiton(query)
        answer = res["answer"]
        
        # answer = change_result(answer)
        if answer is None:
            print(f"id {num}: 输出结果不对".center(60, "*"))
            answer = ""
        else:
            print(f"id {num}: {answer}")
        results[num]["correct_answer"] = answer
        save_one_json = save_folder / f"{num}.json"
        with open(str(save_one_json), "w", encoding="utf-8") as f:
            json.dump(results[num], f, ensure_ascii=False, indent=4)
        papers_id_list.append(query["paper_id"])
        querys_list.append(query["question"])
        nodes_list.append([node.text for node in res["nodes"]])
        scores_list.append([node.score for node in res["nodes"]])

        node_texts = [node.get_content().replace("\n", " ") for node in res["nodes"]]
        topk = len(node_texts)
        topk_columns = [f"top{i+1}" for i in range(topk)]
        row_data = [query["paper_id"]] + [query["question"]] + node_texts + [answer]
        columns = ["paper_id"] + ["query"] + topk_columns + ["answer"]
        all_rows.append(row_data)
    df = pd.DataFrame(all_rows, columns=columns)
    # 保存为 CSV 文件
    df.to_csv(str(save_folder / "retrieved_nodes.csv"), index=True, encoding="utf-8")

    save_json = Path(save_folder) / "base_version.json"
    with open(str(save_json), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    fire.Fire(main)
