# -*-coding:UTF-8 -*-
'''
* notebook.py
* @author wuzm
* created 2025/06/20 21:35:30
* @function: a notebook for testing MultiModal RAG
'''
import os
import requests
from pathlib import Path
from pdf2image import convert_from_path
from byaldi import RAGMultiModalModel
from openai import OpenAI


# pdfs_dir = "/Volumes/wuzhaoming/Dataset/RAG/InstructionPDFs"
# model_dir = "/Volumes/wuzhaoming/Models/VLRAG"
pdfs_dir = "E:/Dataset/RAG/InstructionPDFs"
model_dir = "E:/Models/VLRAG"

pdfs = {
    "MALM": str(Path(pdfs_dir) / "pdfs" / "malm-4-drawer-chest-white__AA-2398381-2-100.pdf"),
    "BILLY": str(Path(pdfs_dir) / "pdfs" / "billy-bookcase-white__AA-1844854-6-2.pdf"),
    "BOAXEL": str(Path(pdfs_dir) / "pdfs" / "boaxel-wall-upright-white__AA-2341341-2-100.pdf"),
    "ADILS": str(Path(pdfs_dir) / "pdfs" / "adils-leg-white__AA-844478-6-2.pdf"),
    "MICKE": str(Path(pdfs_dir) / "pdfs" / "micke-desk-white__AA-476626-10-100.pdf")
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

all_images = convert_pdfs_to_images(str(Path(pdfs_dir) / "pdfs"))
index_name = "image_index"
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

text_query = "How many people are needed to assemble the Malm?"
topk = 3
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
chat_template = [
        {
            "role": "user",
            "content": [{"type": "image_url", "image_url": {"url": f"data:image/png;base64,{result['base64']}"}} for result in results]
            + [{"type": "text", "text": text_query}],
        }
    ]
completion = client.chat.completions.create(
    model="qwen-vl-max",  # 此处以qwen-vl-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    messages=chat_template
)
response = completion.choices[0].message.content
print(f"{response}")
