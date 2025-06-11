# -*-coding:UTF-8 -*-
'''
* injection.py
* @author wuzm
* created 2025/06/11 19:18:03
* @function: 
'''
from typing import List
from llama_index.core import SimpleDirectoryReader
from llama_index.core.schema import Document

def read_data(path: str = "data") -> List[Document]:
    reader = SimpleDirectoryReader(
        input_dir=path,
        recursive=True,
        required_exts=[
            ".pdf"
        ],
        encoding="utf-8"
    )
    return reader.load_data()
