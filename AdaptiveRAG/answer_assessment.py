### Answer Grader
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from prepare import llm

# Data model
class GradeAnswer(BaseModel):
    """Binary score to assess answer addresses question."""

    binary_score: str = Field(description="Answer addresses the question, 'yes' or 'no'")

# Preamble
preamble = """You are a grader assessing whether an answer addresses / resolves a question \n
Give a binary score 'yes' or 'no'. Yes' means that the answer resolves the question."""

# LLM with function call
structured_llm_grader = llm.with_structured_output(GradeAnswer)

# Prompt
answer_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", preamble),
        ("human", "User question: \n\n {question} \n\n LLM generation: {generation}"),
    ]
)

answer_grader = answer_prompt | structured_llm_grader


if __name__ == "__main__":
    question = "types of agent memory"
    from answer_generating import generation
    response = answer_grader.invoke({"question": question,"generation": generation})
    print(response)
