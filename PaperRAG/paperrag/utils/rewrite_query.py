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