QA_TEMPLATE_old = """\
    上下文信息如下：
    ----------
    {context_str}
    ----------
    请你基于上下文信息而不是自己的知识，回答以下问题，问题提供了四个选项，分别使用了A、B、C、D进行表示，你需要从四个选项中选出能够回答问题的选项。该问题可能不仅仅只有一个选项符合需求，可能有多个选项符合。一定要注意不能四个选项都不符合需求，这种情况下你应该尽可能返回一个最符合问题的选项。以json形式返回每一个选项是否能够回答该问题，能够回答的话对应选项返回True，否则返回False。例如：{"A": True, "B": False, "C": True, "D":False}。
    {query_str}

    回答：\
    """

QA_TEMPLATE = """\
你现在是一位大语言模型领域的专家，拥有丰富的科研经验，也发表过大量的SCI论文。接下来我会给你一道大语言模型相关的论文，请根据题干基于上下文信息而不是自己的知识给出正确答案。

可供选择的答案选项总共有4项，分别是A、B、C、D，正确答案都是多项，如AB或ACD或ABCD，没有单选。

你首先一步一步的推理，然后根据题干给出正确答案，不需要给出推理过程，除了答案不要给出其他任何信息。

接下来是2个例子：
例子1:
"question":Which of the following factors may cause multilingual large language models to show English bias when processing non-English languages?\nA. The model's training data mainly consists of English text.\nB. The model uses English as the central language in the middle layer for semantic understanding and reasoning.\nC. In the model's word embedding space, English word embeddings are more densely distributed and easier to be \"captured\" by the model.\nD. The model translates non-English text into English before translating it into the target language.
"correct_answer": "ABC"

例子2:
"question": "The ablation study tests different discriminator models for LLaMA3-8B-Instruct on GSM8\nK. If using GPT-4 as the discriminator improves accuracy from 91.13% (Phi3-Mini) to 92.57%, which of the following is NOT true about the marginal gain compared to using the generator's majority voting baseline (88.70%)?\nA. 3.87%\nB. 1.58%\nC. The gain is statistically insignificant because GPT-4 is not an SLM\nD. Both A and B are correct, but the paper emphasizes absolute gains ",
"correct_answer": "BCD"

接下来是你需要根据查询内容进行回答的问题：

提供的上下文信息：
{context_str}

题干：
{query_str}

回答：\
"""

QA_TEMPLATE_now_best = """\
你现在是一位大语言模型领域的专家，拥有丰富的科研经验，也发表过大量的SCI论文。接下来我会给你一道大语言模型相关的论文，请根据题干基于上下文信息而不是自己的知识给出正确答案。

可供选择的答案选项总共有5项，分别是A、B、C、D，正确答案都是多项，如AB或ACD或ABCD，没有单选。

你首先一步一步的推理，然后根据题干给出正确答案，不需要给出推理过程，除了答案不要给出其他任何信息。

接下来是1个例子：
题干：
Which of the following factors may cause multilingual large language models to show English bias when processing non-English languages?\nA. The model's training data mainly consists of English text.\nB. The model uses English as the central language in the middle layer for semantic understanding and reasoning.\nC. In the model's word embedding space, English word embeddings are more densely distributed and easier to be \"captured\" by the model.\nD. The model translates non-English text into English before translating it into the target language.
答案：ABC

接下来是你要回答的大语言模型知识题：

提供的上下文信息：
{context_str}

题干：
{query_str}

回答：\
"""

QA_TEMPLATE_old1 = """\
你是一位大语言模型领域的专家，拥有丰富的科研经验，也发表过大量的SCI论文。你的任务是根据提供的论文内容回答一道多选题。

请注意：你必须 **严格基于提供的上下文信息** 回答问题，不得使用已有的知识背景或常识。正确选项可能为一个或多个，如 A、AB、ACD 等。

你需要在心中逐项判断每个选项是否被论文内容支持，但**最终只输出选项组合**，不要输出推理过程，不要添加任何额外说明。

以下是一个示例：

---
题干：
Which of the following factors may cause multilingual large language models to show English bias when processing non-English languages?
A. The model's training data mainly consists of English text.
B. The model uses English as the central language in the middle layer for semantic understanding and reasoning.
C. In the model's word embedding space, English word embeddings are more densely distributed and easier to be "captured" by the model.
D. The model translates non-English text into English before translating it into the target language.

回答：ABC
---

现在请回答下面这道题：

提供的上下文信息：
{context_str}

题干：
{query_str}

回答：\
"""



QA_TEMPLATE_0 = """\
你是一名学术助手。以下是从论文中提取的上下文内容：

--------------------
{context_str}
--------------------

请你仅根据上述内容判断以下每个选项是否被论文所支持。使用 JSON 格式返回结果，例如：{"A": true, "B": false, "C": false, "D": true}。

{query_str}
"""

QA_TEMPLATE_1 = """\
你是一名学术助手。以下是论文中与问题相关的内容：

--------------------
{context_str}
--------------------

请你基于上下文信息分析问题，判断哪些选项正确描述了模型的处理过程或机制。请使用 JSON 格式返回，例如：{"A": true, "B": false, "C": true, "D": false}。

{query_str}

"""

QA_TEMPLATE_2 = """\
你是一名学术助手。下面是从论文中提取的上下文内容：

--------------------
{context_str}
--------------------

请你根据上下文判断以下哪些选项正确地描述了问题中提到的术语或概念。请使用 JSON 格式返回，例如：{"A": true, "B": false, "C": true, "D": false}。

{query_str}

"""

QA_TEMPLATE_3 = """\
你是一名学术助手。请根据以下上下文内容回答多选题，仅基于上下文信息作答，不要使用外部知识。请使用 JSON 格式返回每个选项是否正确，例如：{"A": true, "B": false, "C": true, "D": false}。

--------------------
{context_str}
--------------------

{query_str}


"""

QA_TEMPLATE_4 = """\
你是一名学术助手。以下是论文中包含对比的信息片段：

--------------------
{context_str}
--------------------

请你根据上下文内容，判断以下选项中哪些是论文中比较结果的正确描述。使用 JSON 格式返回，例如：{"A": true, "B": false, "C": true, "D": false}。

{query_str}

"""

QA_TEMPLATE_5 = """\
你是一名学术助手。以下是论文中与应用场景相关的内容：

--------------------
{context_str}
--------------------

请判断以下选项中哪些描述了论文中技术或方法的应用场景或作用。请使用 JSON 格式返回结果，例如：{"A": true, "B": false, "C": true, "D": false}。

{query_str}


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