# -*-coding:UTF-8 -*-
'''
* diff.py
* @author wuzm
* created 2025/07/04 16:18:33
* @function: 
'''
import json

if __name__ == "__main__":
    json_path1 = "/Volumes/wuzhaoming/Dataset/TIANCHIPaperRAG/结果/result_bge_m3_vec_top8_multi/base_version.json"
    json_path2 = "/Volumes/wuzhaoming/Dataset/TIANCHIPaperRAG/结果/result_bge_m3_vector_template/base_version.json"
    with open(json_path1, encoding="utf-8") as f:
        infos1 = json.loads(f.read())
    with open(json_path2, encoding="utf-8") as f:
        infos2 = json.loads(f.read())
    for info1, info2 in zip(infos1, infos2):
        info_answer1, info_answer2 = info1["correct_answer"], info2["correct_answer"]
        if info_answer1 != info_answer2:
            print(f"{info1['question']} \n {info_answer1} --- {info_answer2}")
