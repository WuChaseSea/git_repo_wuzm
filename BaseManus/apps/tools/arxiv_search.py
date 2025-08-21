import asyncio
from typing import Optional, List
import arxiv

from pydantic import BaseModel, Field

from apps.tools.base import ToolResult


class ArxivResult(BaseModel):
    """Represents a singel search result returned by as search engine."""

    title: str = Field(default="", description="Title of a single search result")
    link: str = Field(default="", description="Link of a single searched paper")
    abstract: str = Field(default="", description="abstract of a single search paper")

    def __str__(self) -> str:
        """Strin grepresentation of a search result."""
        return f"{self.title}({self.link}) {self.abstract}"


class ArxivResponse(ToolResult):
    """Structured response from arxiv search tool, inh"""
    query: str = Field(description="Arxiv search keywords")
    results: List[ArxivResult] = Field(default_factory=list, description="List of search results")


class ArxivSearch(BaseModel):
    """Class for searching arxiv papers"""

    name: str = "arxiv_search"
    description: str = """
    Search arxiv papers information about provided topic.
    This tool returns comprehensive search results with relevant information, including URLs, titles, and abstract.
    """
    parameters: dict = {
        "type": "object",
        "properties": {
            "query": {
                "type": "list",
                "description": "(required) The search query key point list to search the relevant papers."
            },
            "num_results": {
                "type": "integer",
                "description": "(Optional) The number of search results to return. Default is 5.",
                "default": 5,
            },
        },
    }

    async def execute(
        self,
        query: list,
        num_results: int=5
    ) -> ArxivResponse:
        formmatted_query = " AND ".join(f'all:"{kw.strip()}"' for kw in query)
        search_results = arxiv.Search(
            query=query,
            max_results=num_results,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        results = self.arxiv_client.results(search_results)
        results = list(results)
        results_info  = [
            
        ]
