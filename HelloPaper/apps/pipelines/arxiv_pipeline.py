import arxiv

from .llm_pipeline import LLMPipeline
from apps.base import Document
from apps.utils import Render
from apps.pipelines.templates import SUMMARY_PAPER_BY_ABSTRACT


class ArxivPipeline():

    def __init__(self):
        self.arxiv_client = arxiv.Client()
        self.llm_pipeline = LLMPipeline()
    
    def stream(self, query, max_results):
        search_results = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by = arxiv.SortCriterion.SubmittedDate
        )
        results = self.arxiv_client.results(search_results)
        results = list(results)
        results_info = [
            Document(
                channel="info",
                content=f"{result.summary}",
                metadata={
                    "Title": result.title,
                    "Link": result.links[-1].href
                }
            )
            for result in results
        ]
        results_info = [
            Document(
                channel="info",
                content=Render.collapsible_with_arxiv_result(result, open_collapsible=True)
            ) for result in results_info
        ]
        yield from results_info

        answers = []
        for result in results:
            answer = yield from self.summary_single_paper_by_abstract(result)
            answers.append(answer)
    
    def summary_single_paper_by_abstract(self, result):
        self.llm_pipeline.build_prompt_template(mode="text", desc="summary_abstract", prompt=SUMMARY_PAPER_BY_ABSTRACT)
        var_name = f"template_summary_abstract_text"
        template_text = getattr(self.llm_pipeline, var_name)
        qa_prompt = template_text.format(
            title=result.title,
            abstract=result.summary
        )
        messages = []
        messages.append(
            {
                "role": "user",
                "content": qa_prompt
            }
        )
        print(f"LLM summarying")
        output = ""
        before_output = None
        for out_msg in self.llm_pipeline.llm.chat(messages, stream=True):
            now_output = out_msg[0]["content"]
            if before_output:
                now_output = now_output[len(before_output):]
                before_output += now_output
            else:
                before_output = now_output
            output += now_output
            yield Document(channel="chat", content=now_output)
        print(f"LLM summary ended.")
        answer = Document(text=output)
        return answer
