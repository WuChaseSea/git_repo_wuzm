# -*-coding:UTF-8 -*-
'''
* main.py
* @author wuzm
* created 2025/06/11 14:25:18
* @function: 
'''
import os
import fire

from paperrag.utils import get_yaml_data
from paperrag.pipeline import PaperRAGPipeline


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
    


if __name__ == "__main__":
    fire.Fire(main)