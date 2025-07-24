import string

def format_options(option_list):
    formatted = []
    for i, opt in enumerate(option_list):
        label = string.ascii_uppercase[i]
        formatted.append(f"{label}. {opt.strip()}")
    return "\n".join(formatted)

def rewrite_query(question: str, options: list[str], mode: str = "default") -> str:
    """
    Automatically rewrites a multiple-choice QA query to improve semantic embedding.

    :param question: Original multiple-choice question.
    :param options: List of answer option strings (e.g., ["Option A", "Option B", ...])
    :param mode: Rewrite mode: ["default", "dense", "lite"]
    :return: Rewritten query string.
    """

    formatted_options = format_options(options)

    if mode == "default":
        rewritten = (
            f"The following question concerns technical details discussed in an academic paper. "
            f"Determine which of the following statements are supported by the paper's content.\n\n"
            f"Question:\n{question.strip()}\n\n"
            f"Options:\n{formatted_options}\n\n"
            f"The answer depends on evidence found in the paper, including methodology, results, and discussions."
        )

    elif mode == "dense":
        # 更丰富版本，适合 dense embedding
        rewritten = (
            f"This is a question derived from a scientific paper. Carefully examine the paper to identify which of the following options are supported or refuted by its content.\n\n"
            f"Question:\n{question.strip()}\n\n"
            f"Options:\n{formatted_options}\n\n"
            f"Look for mentions of these concepts in experimental results, methodology sections, or ablation studies."
        )

    elif mode == "lite":
        # 精简版本，适合 embedding 紧凑检索
        opt_keywords = " | ".join([f"{string.ascii_uppercase[i]}" for i in range(len(options))])
        rewritten = (
            f"{question.strip()} Consider whether options {opt_keywords} are supported in the paper."
        )

    else:
        raise ValueError(f"Unknown rewrite mode: {mode}")

    return rewritten

question = "Which evaluation metrics are used to measure KoPA's performance?"
options = ["MRR", "Precision", "Hits@10", "Recall"]

print(rewrite_query(question, options, mode="default"))

import json
from copy import deepcopy
from tqdm import tqdm


if __name__ == '__main__':
    question_file = "/Volumes/wuzhaoming/Dataset/TIANCHIPaperRAG/papar_QA_dataset/multi_choice_questions_class.json"
    with open(question_file, encoding="utf-8") as f:
        queries = json.loads(f.read())
    print(f"开始改写查询...")
    results = deepcopy(queries)
    for num, query in enumerate(tqdm(queries, total=len(queries))):
        query_str = query["question"]
        question_str = query_str.split('A.')[0].strip()
        answer_a = query_str.split('A.')[1].split('B.')[0].strip()
        answer_b = query_str.split('A.')[1].split('B.')[1].split('C.')[0].strip()
        answer_c = query_str.split('A.')[1].split('B.')[1].split('C.')[1].split('D.')[0].strip()
        answer_d = query_str.split('D.')[1].strip()
        options = [answer_a, answer_b, answer_c, answer_d]
        rewrite_result = rewrite_query(question_str, options, mode="default")
        results[num]["question"] = rewrite_result
    save_json = "/Volumes/wuzhaoming/Dataset/TIANCHIPaperRAG/papar_QA_dataset/multi_choice_questions_class_rewrite.json"
    with open(str(save_json), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
