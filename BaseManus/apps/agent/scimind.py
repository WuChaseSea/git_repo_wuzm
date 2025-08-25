from typing import Dict, List, Optional

from pydantic import Field, model_validator

from apps.agent.toolcall import ToolcallAgent
from apps.prompts.scimind import SYSTEM_PROMPT, NEXT_STEP_PROMPT
from apps.config import config
from apps.tools import (
    ToolCollection,
    Terminate,
    ArxivSearch,
    StrReplaceEditor,
    CreateChatCompletion,
)
from apps.logger import logger


class SCIMind(ToolcallAgent):
    """A versatile general-purpose sci agent with support for local tools."""

    name: str = "SCIMind"
    description: str = "A versatile agent that can solve various tasks about SCI using multiple tools"

    system_prompt: str = SYSTEM_PROMPT.format(directory=config.workspace_root)
    next_step_prompt: str = NEXT_STEP_PROMPT

    max_observe: int = 10000
    max_steps: int = 20

    # Add general-purpose tools to the tool collection
    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(
            StrReplaceEditor(),
            ArxivSearch(),
            Terminate(),
        )
    )

    special_tool_names: list[str] = Field(default_factory=lambda: [Terminate().name])

    @classmethod
    async def create(cls, **kwargs) -> "SCIMind":
        """Factory method to create  an dproperly initialize a SCIMind instance"""
        instance = cls(**kwargs)
        return instance
    
    async def cleanup(self):
        """Clean up resources used by the agent's tools."""
        logger.info(f"🧹 Cleaning up resources for agent '{self.name}'...")
        # TODO
        # Add cleanup operations
