# -*-coding:UTF-8 -*-
'''
* notebook_paper.py
* @author wuzm
* created 2025/06/21 10:58:31
* @function: a notebook for testing MultiModal PaperRAG
'''
import os
import json
import re
from pathlib import Path
from pdf2image import convert_from_path
from byaldi import RAGMultiModalModel
from openai import OpenAI


# pdfs_dir = "/Volumes/wuzhaoming/Dataset/RAG/InstructionPDFs"
# model_dir = "/Volumes/wuzhaoming/Models/VLRAG"
pdfs_dir = "E:/Dataset/RAG/Papers"
model_dir = "E:/Models/VLRAG"

pdfs = {
    "0": str(Path(pdfs_dir) / "pdfs" / "0" / "2024.acl-long.820.pdf")
}

def convert_pdfs_to_images(pdf_folder):
    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf") and f[0]!="."]
    all_images = {}
    for doc_id, pdf_file in enumerate(pdf_files):
        pdf_path = Path(pdf_folder) / pdf_file
        images = convert_from_path(str(pdf_path))
        
        print(f"{doc_id}: {pdf_file} read success.")
        all_images[doc_id] = images
    
    return all_images

all_images = convert_pdfs_to_images(str(Path(pdfs_dir) / "pdfs" / "0"))
index_name = "paper_index"
if (Path(".byaldi") / index_name).exists():
    docs_retrieval_model = RAGMultiModalModel.from_index(index_name)
else:
    docs_retrieval_model = RAGMultiModalModel.from_pretrained(str(Path(model_dir) / "colpali-v1.2"))
    docs_retrieval_model.index(
        input_path=str(Path(pdfs_dir) / "pdfs"),
        index_name=index_name,
        store_collection_with_index=True,
        overwrite=True
    )

text_query = "Which of the following factors may cause multilingual large language models to show English bias when processing non-English languages?\nA. The model's training data mainly consists of English text.\nB. The model uses English as the central language in the middle layer for semantic understanding and reasoning.\nC. In the model's word embedding space, English word embeddings are more densely distributed and easier to be \"captured\" by the model.\nD. The model translates non-English text into English before translating it into the target language."
topk = 8
results = docs_retrieval_model.search(text_query, k=topk)

def get_grouped_images(results, all_images):
    grouped_images = []
    for result in results:
        doc_id = result["doc_id"]
        page_num = result["page_num"]
        grouped_images.append(
            all_images[doc_id][page_num - 1]
        )  # page_num are 1-indexed, while doc_ids are 0-indexed. Source https://github.com/AnswerDotAI/byaldi?tab=readme-ov-file#searching

    return grouped_images

grouped_images = get_grouped_images(results, all_images)

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

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
            "content": [{"type": "image_url", "image_url": {"url": f"data:image/png;base64,{result['base64']}"}} for result in results]
            + [{"type": "text", "text": QA_TEMPLATE}],
        }
    ]
completion = client.chat.completions.create(
    model="qwen-vl-plus",  # 此处以qwen-vl-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    messages=chat_template
)
response = completion.choices[0].message.content

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

answer = extract_json_block(response)

print(f"answer is: {answer}")