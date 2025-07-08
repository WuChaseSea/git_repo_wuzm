from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import chat_agent_executor
from langchain_core.messages import HumanMessage
tools = [TavilySearchResults(max_results=1)]
model = ChatTongyi()
app = chat_agent_executor.create_tool_calling_executor(model, tools)
app.get_graph().print_ascii()