from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from prepare import llm

# Data model
class web_search(BaseModel):
    """
    The internet. Use web_search for questions that are related to anything else than agents, prompt engineering, and adversarial attacks.
    """
    query: str = Field(description="The query to use when searching the internet.")

class vectorstore_search(BaseModel):
    """
    A vectorstore containing documents related to agents, prompt engineering, and adversarial attacks. Use the vectorstore for questions on these topics.
    """
    query: str = Field(description="The query to use when searching the vectorstore.")

# Preamble
preamble = """You are an expert at routing a user question to a vectorstore or web search.
The vectorstore contains documents related to agents, prompt engineering, and adversarial attacks.
Use the vectorstore for questions on these topics. Otherwise, use web-search."""

# LLM with tool use and preamble
structured_llm_router = llm.bind_tools(tools=[web_search, vectorstore_search], preamble=preamble)

# Prompt
route_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{question}"),
    ]
)

question_router = route_prompt | structured_llm_router

if __name__ == "__main__":
    response = question_router.invoke({"question": "Who will the Bears draft first in the NFL draft?"})
    print(response.tool_calls)
    response = question_router.invoke({"question": "What are the types of agent memory?"})
    print(response.tool_calls)
    response = question_router.invoke({"question": "Hi how are you?"})
    print(response.tool_calls)
