import arxiv

from .llm_pipeline import LLMPipeline
from apps.base import Document
from apps.utils import Render
from apps.pipelines.templates import SUMMARY_PAPER_BY_ABSTRACT


class ArxivPipeline():

    def __init__(self):
        self.arxiv_client = arxiv.Client()
        self.llm = LLMPipeline()
    
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

        for result in results:
            answer = self.summary_single_paper_by_abstract(result)
    
    def summary_single_paper_by_abstract(self, result):
        self.llm.build_prompt_template(mode="text", desc="summary_abstract", prompt=SUMMARY_PAPER_BY_ABSTRACT)
        var_name = f"template_summary_abstract_text"
        template_text = getattr(self.llm, var_name)
        template_text.format(
            title=result.title,
            abstract=result.summary
        )
        import ipdb;ipdb.set_trace()
