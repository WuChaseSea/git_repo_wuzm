import string

def format_options(option_list):
    formatted = []
    for i, opt in enumerate(option_list):
        label = string.ascii_uppercase[i]
        formatted.append(f"{label}. {opt.strip()}")
    return "\n".join(formatted)

def guess_question_type(question: str) -> str:
    """
    Try to guess the type of the question for better template selection.
    """
    q = question.lower()
    if "metric" in q or "score" in q or "accuracy" in q:
        return "evaluation"
    elif "component" in q or "module" in q or "architecture" in q:
        return "component"
    elif "ablation" in q or "improvement" in q or "effect" in q:
        return "ablation"
    elif "experiment" in q:
        return "experiment"
    return "general"


def rewrite_query(question: str, options: list[str], mode: str = "default") -> str:
    """
    Automatically rewrites a multiple-choice QA query to improve semantic embedding.

    :param question: Original multiple-choice question.
    :param options: List of answer option strings (e.g., ["Option A", "Option B", ...])
    :param mode: Rewrite mode: ["default", "dense", "lite"]
    :return: Rewritten query string.
    """

    formatted_options = format_options(options)
    qtype = guess_question_type(question)

    # Default version
    default_view = (
        f"The following question concerns technical details discussed in an academic paper. "
        f"Determine which of the following statements are supported by the paper's content.\n\n"
        f"Question:\n{question.strip()}\n\n"
        f"Options:\n{formatted_options}\n\n"
        f"The answer depends on evidence found in the paper, including methodology, results, and discussions."
    )


    # Specialized version based on question type
    if qtype == "evaluation":
        type_view = (
            f"Identify which of the following metrics or criteria were used to evaluate the proposed method in the paper.\n\n"
            f"Question:\n{question.strip()}\n\n"
            f"Options:\n{formatted_options}\n\n"
            f"Focus on the experimental section or result tables."
        )
    elif qtype == "component":
        type_view = (
            f"Determine which components or modules are explicitly mentioned as part of the proposed system.\n\n"
            f"Question:\n{question.strip()}\n\n"
            f"Options:\n{formatted_options}\n\n"
            f"Focus on architecture descriptions and methodology sections."
        )
    elif qtype == "ablation":
        type_view = (
            f"Based on the ablation studies in the paper, identify which of the following statements are supported.\n\n"
            f"Question:\n{question.strip()}\n\n"
            f"Options:\n{formatted_options}\n\n"
            f"Look into ablation study results and related performance changes."
        )
    else:
        type_view = default_view  # fallback


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

import random

def generate_multi_perspective_queries(qa_list):
    """
    给定一个包含问题和选项的列表，自动生成更有利于向量检索的多视角拼接查询语句。
    
    参数：
        qa_list: List[Dict]，每个元素形如：
            {
                "question": "原始问题字符串",
                "options": ["A. 选项1", "B. 选项2", ...]
            }

    返回：
        List[Dict]，每个元素形如：
            {
                "original_question": "...",
                "multi_view_query": "拼接后的查询"
            }
    """

    # 多视角引导语句模板
    perspectives = [
        "Based on the experimental results discussed in the paper,",
        "Considering the evaluation section of the study,",
        "From the methodology and reported findings,",
        "According to the performance metrics highlighted by the authors,",
        "In the context of the reported evaluation on benchmark datasets,"
    ]

    # 查询重构模板
    reform_templates = [
        "does the paper mention metrics such as {opt}?",
        "which of the following metrics are explicitly reported: {opt}?",
        "are metrics like {opt} used to assess the model's performance?",
        "is there any mention of evaluation metrics including {opt}?",
        "does the analysis involve metrics like {opt}?"
    ]

    output = []

    for qa in qa_list:
        question = qa['question'].strip()
        
        # 去除选项中的"A. "等前缀，仅保留选项文本
        raw_options = [opt.split('. ', 1)[-1] for opt in qa['options']]
        options_str = ', '.join(raw_options)

        # 随机选择视角与改写方式
        perspective = random.choice(perspectives)
        reformulation = random.choice(reform_templates).format(opt=options_str)

        # 构建完整的多视角查询
        multi_view_query = (
            f"{question} {perspective} {reformulation} "
            f"How does the paper evaluate the proposed method?"
        )

        output.append({
            "original_question": question,
            "multi_view_query": multi_view_query
        })

    return output

