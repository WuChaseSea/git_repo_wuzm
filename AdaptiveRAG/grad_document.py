from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from prepare import retriever, llm

### Retrieval Grader

# Data model
class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""

    binary_score: str = Field(description="Documents are relevant to the question, 'yes' or 'no'")

# Prompt
preamble = """You are a grader assessing relevance of a retrieved document to a user question. \n
If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n
Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."""

# LLM with function call
structured_llm_grader = llm.with_structured_output(GradeDocuments)

grade_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", preamble),
        ("human", "Retrieved document: \n\n {document} \n\n User question: {question}"),
    ]
)

retrieval_grader = grade_prompt | structured_llm_grader


if __name__ == "__main__":
    question = "types of agent memory"
    docs = retriever.invoke(question)
    doc_txt = docs[1].page_content
    # response =  retrieval_grader.invoke({"question": question, "document": doc_txt})
    # print(response)
