from typing import Optional, List, Any

from pydantic import BaseModel, Field, model_validator, PrivateAttr

from apps.tools.base import BaseTool, ToolResult
from apps.schema import Message


class SummaryResponse(ToolResult):
    """Structured response from summary tool"""
    query: str = Field(description="user command")
    results: str = Field(description="summary result by llm")

    @model_validator(mode="after")
    def popupate_output(self) -> "SummaryResponse":
        """Popupate output or error fields based on summary results."""
        if self.error:
            return self
        
        self.output = self.results
        return self


class SummaryAnswer(BaseTool):
    """Class for summarizing user answer"""

    name: str = "summary_answer"
    description: str = """
    Summarize and answer the user's questions according to the existing information.
    This tool returns formmatted answer according to user's text.
    """
    parameters: dict = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "(required) The query text represents user's command"
            },
            "provided_info": {
                "type": "list",
                "description": "(Optional) The information obtained from previous operations is used to satisfy user needs"
            },
        }
    }

    _llm: Any = PrivateAttr(default=None)

    @classmethod
    def with_llm(cls, llm, **kwargs):
        inst = cls(**kwargs)
        inst._llm = llm
        return inst
    
    async def execute(
        self,
        query: str,
        provided_info: list=None
    ) -> SummaryResponse:
        msgs = Message.assistant_message("You are a helpful assistant.")
        msgs += Message.user_message(
            f"""Please summary the provided info to get the final answer according to user's prompt.
            User's Prompt: {query}
            Provided ino: {provided_info}
            """
        )
        response = await self._llm.ask(messages=msgs, stream=True)
        
        return SummaryResponse(query=query, results=response)
