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
from paperrag.custom.parser import PDFParser

data_dir = "E:/Dataset/TIANCHIPaperRAG/papar_QA_dataset"
pdf_parser = PDFParser(
    output_dir=(Path(data_dir) / "pdf_parser")
)
pdf_parser.parse_and_export(input_doc_paths=str(Path(data_dir) / "papers"/ "0" / "2024.acl-long.820.pdf"))
