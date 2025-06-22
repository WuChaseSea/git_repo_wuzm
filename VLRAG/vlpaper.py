# -*-coding:UTF-8 -*-
'''
* vlpaper.py
* @author wuzm
* created 2025/06/21 11:52:30
* @function: Papers RAG system
'''
import os
import json
import re
from pathlib import Path
from pdf2image import convert_from_path
from byaldi import RAGMultiModalModel
from openai import OpenAI
from tqdm import tqdm
from copy import deepcopy
from datetime import datetime


def extract_correct_options(response_str):
    try:
        # 将字符串转换为字典
        result = json.loads(response_str)
        # 提取所有为 True 的 key，即正确选项
        correct_options = [k for k, v in result.items() if v is True]
        return ''.join(sorted(correct_options))
    except Exception as e:
        print("解析失败：", e)
        return ""

def extract_json_block(text):
    try:
        # 使用正则提取类似 JSON 格式的字符串
        match = re.search(r'{[^{}]*}', text)
        if match:
            return extract_correct_options(match.group(0))
    except Exception as e:
        print("提取失败：", e)
    return []


# 将所有PDF做成索引
pdfs_dir = "E:/Dataset/TIANCHIPaperRAG/papar_QA_dataset"
model_dir = "E:/Models/VLRAG"
index_name = "paper86_index"
if (Path(".byaldi") / index_name).exists():
    docs_retrieval_model = RAGMultiModalModel.from_index(index_name)
else:
    docs_retrieval_model = RAGMultiModalModel.from_pretrained(str(Path(model_dir) / "colpali-v1.2"))
    docs_retrieval_model.index(
        input_path=str(Path(pdfs_dir) / "papers"),
        index_name=index_name,
        store_collection_with_index=True,
        overwrite=True
    )

question_file = str(Path(pdfs_dir) / "multi_choice_questions.json")
with open(question_file, encoding="utf-8") as f:
    queries = json.loads(f.read())
print(f"开始生成答案...")
results = deepcopy(queries)
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
save_folder = Path(pdfs_dir) / f"result_{current_time}"

# save_folder = Path(config["work_dir"]) / f"result_2025-06-19_20-45-51"
save_folder.mkdir(parents=True, exist_ok=True)
topk = 8
client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)
for num, query in enumerate(tqdm(queries, total=len(queries))):
    text_query = query["question"]
    image_results = docs_retrieval_model.search(text_query, k=topk)
    QA_TEMPLATE = f"""
    请你仅根据提供的图片信息，而非你自己的知识，回答以下选择题。

    问题共有四个选项（A、B、C、D），可能有多个正确选项，也可能只有一个。请逐个判断每个选项是否可以根据图片中的信息进行支持。

    请按照以下格式返回答案：
    {{
        "A": true 或 false,
        "B": true 或 false,
        "C": true 或 false,
        "D": true 或 false
    }}

    注意事项：
    1. 如果图片中没有明确的信息支持某个选项，应标记为 false；
    2. 如果确实找不到明确支持的选项，也必须返回一个最可能的选项为 true，其他为 false；
    3. 严禁凭借常识或推测作答，所有判断必须来自图像信息。

    问题如下：
    {text_query}
    """
    chat_template = [
        {
            "role": "user",
            "content": [{"type": "image_url", "image_url": {"url": f"data:image/png;base64,{result['base64']}"}} for result in image_results]
            + [{"type": "text", "text": QA_TEMPLATE}],
        }
    ]
    completion = client.chat.completions.create(
        model="qwen-vl-max-latest", 
        messages=chat_template
    )
    response = completion.choices[0].message.content
    answer = extract_json_block(response)

    print(f"answer is: {answer}")
    results[num]["correct_answer"] = answer
    save_one_json = save_folder / f"{num}.json"
    with open(str(save_one_json), "w", encoding="utf-8") as f:
        json.dump(results[num], f, ensure_ascii=False, indent=4)

save_json = Path(save_folder) / "base_version.json"
with open(str(save_json), "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=4)
