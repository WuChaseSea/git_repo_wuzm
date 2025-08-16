from theflow import Node
from textwrap import dedent

from .base import BaseReasoning
from apps.base import BaseComponent, Document, SystemMessage, HumanMessage, AIMessage, RetrievedDocument
from apps.llms import ChatLLM
from apps.llms.manager import llms
from apps.pipelines import FilePipeline, LLMPipeline
from apps.utils import get_node_content, replace_think_tag_with_details
from apps.utils import Render


class AddQueryContextPipeline(BaseComponent):

    n_last_interactions: int = 5
    llm: ChatLLM = Node(default_callback=lambda _: llms.get_default())

    def run(self, question: str, history: list) -> Document:
        messages = [
            SystemMessage(
                content="Below is a history of the conversation so far, and a new "
                "question asked by the user that needs to be answered by searching "
                "in a knowledge base.\nYou have access to a Search index "
                "with 100's of documents.\nGenerate a search query based on the "
                "conversation and the new question.\nDo not include cited source "
                "filenames and document names e.g info.txt or doc.pdf in the search "
                "query terms.\nDo not include any text inside [] or <<>> in the "
                "search query terms.\nDo not include any special characters like "
                "'+'.\nIf the question is not in English, rewrite the query in "
                "the language used in the question.\n If the question contains enough "
                "information, return just the number 1\n If it's unnecessary to do "
                "the searching, return just the number 0."
            ),
            HumanMessage(content="How did crypto do last year?"),
            AIMessage(
                content="Summarize Cryptocurrency Market Dynamics from last year"
            ),
            HumanMessage(content="What are my health plans?"),
            AIMessage(content="Show available health plans"),
        ]
        for human, ai in history[-self.n_last_interactions :]:
            messages.append(HumanMessage(content=human))
            messages.append(AIMessage(content=ai))

        messages.append(HumanMessage(content=f"Generate search query for: {question}"))

        resp = self.llm(messages).text
        if resp == "0":
            return Document(content="")

        if resp == "1":
            return Document(content=question)

        return Document(content=resp)


class FullQAPipeline(BaseReasoning):
    """Question answering pipeline. Handle from question to answer"""

    file_pipeline: FilePipeline
    llm_pipeline: LLMPipeline

    def __init__(self, file_pipeline, llm_pipeline):
        self.file_pipeline = file_pipeline
        self.llm_pipeline = llm_pipeline

    def stream(
            self, message: str, history: list
    ):
        docs, infos = self.retrieve(message, history)
        print(f"Got {len(docs)} retrieved documents.")
        yield from infos

        context_str = self.prepare_content(docs=docs)
        answer = yield from self.llm_pipeline.stream(
            question=message,
            history=history,
            context=context_str
        )
        processed_answer = replace_think_tag_with_details(answer.text)
        if processed_answer != answer.text:
            yield Document(channel="chat", content=None)
            yield Document(channel="chat", content=processed_answer)
        print(f"answer finished...")
        
        yield from self.show_citations_and_addons(answer=answer, docs=docs, question=message)
        
        return answer
    
    def retrieve(self, message, history):
        retriever_docs = self.file_pipeline.retrieve(query_str=message)
        retriever_docs = [
            RetrievedDocument(
                id=doc.id_,
                embedding=doc.embedding,
                text=doc.text,
                metadata=doc.metadata,
                score=doc.score
            ) for doc in retriever_docs
        ]

        docs, doc_ids = [], []
        plot_docs = []
        retriever_docs_text, retriever_docs_plot = [], []

        for doc in retriever_docs:
            if doc.metadata.get("type", "") == "plot":
                retriever_docs_plot.append(doc)
            else:
                retriever_docs_text.append(doc)
        
        for doc in retriever_docs_text:
            if doc.id_ not in doc_ids:
                docs.append(doc)
                doc_ids.append(doc.id_)
        
        plot_docs.extend(retriever_docs_plot)

        info = [
            Document(
                channel="info",
                content=Render.collapsible_with_header(doc, open_collapsible=True)
            )
            for doc in docs
        ] + [
            Document(
                channel="plot",
                content=doc.metadata.get("data", "")
            )
            for doc in plot_docs
        ]
        
        return docs, info
    
    def prepare_content(self, docs):
        contents = [get_node_content(doc) for doc in docs]
        context_str = "\n\n".join(
            [f"### 文档{i}: {content}" for i, content in enumerate(contents)]
        )
        return context_str
    
    def show_citations_and_addons(self, answer, docs, question):
        print(f"preparing midmap...")
        mindmap_output = self.prepare_mindmap(answer)
        print(f"mindmap prepared...")
        # yield Document(channel="info_mindmap", content=None)  # 清空 info pannel中之前的内容
        if mindmap_output:
            yield mindmap_output
    
    def prepare_mindmap(self, answer) -> Document | None:
        mindmap = answer.metadata["mindmap"]
        if mindmap:
            mindmap_text = mindmap.text
            mindmap_svg = dedent(
                """
                <div class="markmap">
                <script type="text/template">
                ---
                markmap:
                    colorFreezeLevel: 2
                    activeNode:
                        placement: center
                    initialExpandLevel: 4
                    maxWidth: 200
                ---
                {}
                </script>
                </div>
                """
            ).format(mindmap_text)

            mindmap_content = Document(
                channel="info_mindmap",
                content=Render.collapsible(
                    header="""
                    <i>Mindmap</i>
                    <a href="#" id='mindmap-toggle'>
                        [Expand]</a>
                    <a href="#" id='mindmap-export'>
                        [Export]</a>""",
                    content=mindmap_svg,
                    open=True,
                ),
            )
        else:
            mindmap_content = None

        return mindmap_content
