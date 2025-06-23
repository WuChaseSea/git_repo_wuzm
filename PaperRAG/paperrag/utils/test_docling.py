# -*-coding:UTF-8 -*-
'''
* test_docling.py
* @author wuzm
* created 2025/06/22 17:54:12
* @function: test docling 
'''
import sys
sys.path.append("./")
from pathlib import Path
from tqdm import tqdm
from paperrag.custom.parser import PDFParser

# data_dir = "E:/Dataset/TIANCHIPaperRAG/papar_QA_dataset"
data_dir = "/Volumes/wuzhaoming/Dataset/TIANCHIPaperRAG/papar_QA_dataset"
# pdf_parser = PDFParser(
#     output_dir=(Path(data_dir) / "pdf_parser")
# )
# pdf_parser.parse_and_export(input_doc_paths=[(Path(data_dir) / "papers"/ "0" / "2024.acl-long.820.pdf")])

input_doc_paths = [f for f in (Path(data_dir) / "papers").rglob("*.pdf") if not f.name.startswith("._")]
json_folder = "/Volumes/wuzhaoming/Dataset/TIANCHIPaperRAG/papar_QA_dataset/pdf_parser"
names = [i.stem for i in input_doc_paths]
import ipdb;ipdb.set_trace()
for input_path in tqdm(input_doc_paths):
    json_path = Path(json_folder) / (input_path.stem + ".json")
    if not json_path.exists():
        print(input_path.name)
