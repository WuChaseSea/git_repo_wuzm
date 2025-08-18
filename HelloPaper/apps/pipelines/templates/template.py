SYSTEM_PROMPT = "This is a question answering system."

DEFAULT_QA_TEXT_PROMPT = (
    "Use the following pieces of context to answer the question at the end in detail with clear explanation. "  # noqa: E501
    "If you don't know the answer, just say that you don't know, don't try to "
    "make up an answer. Give answer in "
    "{lang}.\n\n"
    "{context}\n"
    "Question: {question}\n"
    "Helpful Answer:"
)

SUMMARY_PAPER_BY_ABSTRACT = """
你是一个有帮助的 AI 研究助手，可以帮助我构建每日论文推荐系统。

以下是我从昨天的 arXiv 爬取的论文，我为你提供了标题和摘要：
标题: {title}
摘要: {abstract}

请对这篇论文进行深入分析，并严格按照以下JSON格式返回你的评估结果。你的分析必须包含以下几个部分：

**结构化分析 (summary_text)**: 提供一个结构化的分析，必须包含以下四个部分的字符串字段：
*   `research_background`: 这项研究试图解决什么核心问题？它在哪个领域背景下展开？
*   `method_and_innovation`: 作者提出了什么新的方法、模型或技术？其核心创新点是什么？
*   `experiment_and_performance`: 通过实验得出了哪些关键结果？与现有方法相比，性能如何？
*   `conclusion_and_significance`: 这项研究得出了什么结论？它对学术界或工业界有什么潜在的意义或影响？

请严格按照以下 JSON 格式返回你的回答，不要添加任何额外的解释或文本：
{{
    "summary_text": {{
        "research_background": "<详细的研究背景和问题分析>",
        "method_and_innovation": "<详细的主要方法和创新点分析>",
        "experiment_and_performance": "<详细的实验结果和性能分析>",
        "conclusion_and_significance": "<详细的结论和意义分析>"
    }}
}}
"""
