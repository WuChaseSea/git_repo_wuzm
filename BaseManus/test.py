# -*-coding:UTF-8 -*-
'''
* test.py
* @author wuzm
* created 2025/08/18 14:43:26
* @function: debug file
'''
import asyncio

from apps.tools.web_search import WebSearch


if __name__ == "__main__":
    web_search = WebSearch()
    search_response = asyncio.run(
        web_search.execute(
            query="python programming", fetch_content=True, num_results=1
        )
    )
    print(search_response.output)