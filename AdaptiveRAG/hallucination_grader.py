### Hallucination Grader
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from prepare import llm

# Data model
class GradeHallucinations(BaseModel):
    """Binary score for hallucination present in generation answer."""

    binary_score: str = Field(description="Answer is grounded in the facts, 'yes' or 'no'")

# Preamble
preamble = """You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved facts. \n
Give a binary score 'yes' or 'no'. 'Yes' means that the answer is grounded in / supported by the set of facts."""

# LLM with function call
structured_llm_grader = llm.with_structured_output(GradeHallucinations)

# Prompt
hallucination_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", preamble),
        ("human", "Set of facts: \n\n {documents} \n\n LLM generation: {generation}"),
    ]
)

hallucination_grader = hallucination_prompt | structured_llm_grader


if __name__ == "__main__":
    from grad_document import docs
    from answer_generating import generation
    response = hallucination_grader.invoke({"documents": docs, "generation": generation})
    print(f"幻觉评估：")
    print(response)
