QA_TEMPLATE = """\
    上下文信息如下：
    ----------
    {context_str}
    ----------
    请你基于上下文信息而不是自己的知识，回答以下问题，问题提供了四个选项，分别使用了A、B、C、D进行表示，你需要从四个选项中选出能够回答问题的选项。该问题可能不仅仅只有一个选项符合需求，可能有多个选项符合。同时，你需要注意不能四个选项都不符合需求，这种情况下你应该尽可能返回一个最符合问题的选项。以json形式返回每一个选项是否能够回答该问题，能够回答的话对应选项返回True，否则返回False。例如：{"A": True, "B": False, "C": True, "D":False}。
    {query_str}

    回答：\
    """

QA_TEMPLATE_EN = """\
Please answer the following question based **only on the provided context**, not on your own knowledge.

【Context】
--------------------
{context_str}
--------------------

【Task Instructions】
You will be given a multiple-choice question with four options: A, B, C, and D.  
Your task is to identify which options are **supported by the context**.

Notes:
1. There may be more than one correct option.  
2. There will always be at least one correct option. Do not output all False.  
3. If an option is clearly supported by the context, mark it as True.  
4. If an option is not mentioned or not supported, mark it as False.  
5. Do not rely on common sense or outside knowledge—use **only the given context**.  

【Question and Options】
{query_str}

【Output Format】
Return a JSON object like this (do not add extra explanation):
{{"A": true, "B": false, "C": true, "D": false}}

【Your Answer】
"""

MERGE_TEMPLATE = """\
    上下文：
    ----------
    {context_str}
    ----------

    你将看到一个问题，和这个问题对应的参考答案

    请基于上下文知识而不是自己的知识补充参考答案，让其更完整地回答问题

    请注意，严格保留参考答案的每个字符，并将补充的内容和参考答案合理地合并，输出更长更完整的包含更多术语和分点的新答案

    请注意，严格保留参考答案的每个字符，并将补充的内容和参考答案合理地合并，输出更长更完整的包含更多术语和分点的新答案

    请注意，严格保留参考答案的每个字符，并将补充的内容和参考答案合理地合并，输出更长更完整的包含更多术语和分点的新答案

    问题：
    {query_str}

    参考答案：
    {answer_str}

    新答案：\
    """