import asyncio
from app.tool.web_search import WebSearch

web_search = WebSearch()
search_response = asyncio.run(
    web_search.execute(
        query="Python programming", fetch_content=True, num_results=1
    )
)
search_response.populate_output()
print(search_response.output)
# print(search_response._fetch_content_for_results())
