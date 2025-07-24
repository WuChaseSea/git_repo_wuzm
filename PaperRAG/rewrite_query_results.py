import json
from copy import deepcopy
from tqdm import tqdm


if __name__ == '__main__':
    question_file = "/Volumes/wuzhaoming/Dataset/TIANCHIPaperRAG/papar_QA_dataset/multi_choice_questions_class.json"
    with open(question_file, encoding="utf-8") as f:
        queries = json.loads(f.read())
    
    answer_file = "/Volumes/wuzhaoming/Dataset/TIANCHIPaperRAG/result_bge_m3_vector8_fusai_rewritequery/base_version.json"
    with open(answer_file, encoding="utf-8") as f:
        answers = json.loads(f.read())
    print(f"开始合并结果...")
    results = deepcopy(queries)
    for num, query in enumerate(tqdm(queries, total=len(queries))):
        results[num]["correct_answer"] = answers[num]["correct_answer"]
    save_json = "/Volumes/wuzhaoming/Dataset/TIANCHIPaperRAG/result_bge_m3_vector8_fusai_rewritequery/base_version_1.json"
    with open(str(save_json), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
