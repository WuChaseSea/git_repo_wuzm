### LLM fallback

from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage

from prepare import llm


# Preamble
preamble = """You are an assistant for question-answering tasks. Answer the question based upon your knowledge. Use three sentences maximum and keep the answer concise."""

# Prompt
prompt = lambda x: ChatPromptTemplate.from_messages(
    [
        HumanMessage(
            f"Question: {x['question']} \nAnswer: "
        )
    ]
)

# Chain
llm_chain = prompt | llm | StrOutputParser()

# Run
question = "Hi how are you?"


if __name__ == "__main__":
    generation = llm_chain.invoke({"question": question})
    print(generation)
