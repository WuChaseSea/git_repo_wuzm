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


pdfs_dir = "/Volumes/wuzhaoming/Dataset/RAG/InstructionPDFs"
model_dir = "/Volumes/wuzhaoming/Models/VLRAG"

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

docs_retrieval_model = RAGMultiModalModel.from_pretrained(str(Path(model_dir) / "colpali-v1.2"))
docs_retrieval_model.index(
    input_path=str(Path(pdfs_dir) / "pdfs"), index_name="image_index", store_collection_with_index=False, overwrite=True
)
text_query = "How many people are needed to assemble the Malm?"

results = docs_retrieval_model.search(text_query, k=3)

def get_grouped_images(results, all_images):
    grouped_images = []

    for result in results:
        doc_id = result["doc_id"]
        page_num = result["page_num"]
        grouped_images.append(
            all_images[doc_id][page_num - 1]
        )  # page_num are 1-indexed, while doc_ids are 0-indexed. Source https://github.com/AnswerDotAI/byaldi?tab=readme-ov-file#searching

    return grouped_images

import ipdb;ipdb.set_trace()
grouped_images = get_grouped_images(results, all_images)
