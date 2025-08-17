import arxiv

from .llm_pipeline import LLMPipeline

class ArxivPipeline():

    def __init__(self):
        self.arxiv_client = arxiv.Client()
        self.llm = LLMPipeline()
    
    def run(self, query, max_results):
        search_results = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by = arxiv.SortCriterion.SubmittedDate
        )
        results = self.arxiv_client.results(search_results)
        results = list(results)
        results_info = [
            {
                "title": result.title,
                "summary": result.summary,
                "link": result.links[-1].href
            }
            for result in results
        ]

        import ipdb;ipdb.set_trace()
