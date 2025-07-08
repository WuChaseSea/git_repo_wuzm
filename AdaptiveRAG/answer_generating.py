### Generate

from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate

from prepare import llm


# Preamble
preamble = """You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise."""

# Prompt
prompt = lambda x: ChatPromptTemplate.from_messages(
    [
        ("system", preamble),
        HumanMessage(
            f"Question: {x['question']} \nAnswer: ",
            additional_kwargs={"documents": x["documents"]},
        )
    ]
)

# Chain
rag_chain = prompt | llm | StrOutputParser()


if __name__ == "_main__":
    # Run
    from grad_document import docs, question
    generation = rag_chain.invoke({"documents": docs, "question": question})
    print(generation)
