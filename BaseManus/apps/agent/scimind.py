from typing import Dict, List, Optional, Any

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
from apps.schema import AgentState


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

    async def run_stream(self, request: Optional[str] = None) -> Any:
        """Execute the agent's main loop asynchronously and yield every step result.

        Args:
            request: Optional initial user request to process.
        
        Returns:
            A string summarizing the execution results.
        
        Raises:
            RuntimeError: If the agent is not in IDLE state at start.
        """
        if self.state != AgentState.IDLE:
            raise RuntimeError(f"Cannot run agent from state: {self.state}")
        
        if request:
            self.update_memory("user", request)
        
        step_executed = False
        async with self.state_context(AgentState.RUNNING):
            while (
                self.current_step < self.max_steps and self.state != AgentState.FINISHED
            ):
                self.current_step += 1
                logger.info(f"Executing step {self.current_step}/{self.max_steps}")
                step_result = await self.step()
                step_output = "\n".join(step_result.split("\n")[1:])
                step_executed = True

                if self.is_stuck():
                    self.handle_stuck_state()
                
                step_result = f"Step {self.current_step}: {step_result}"
                if self.state == AgentState.FINISHED:
                    yield (step_result, "")
                else:
                    yield (step_result, step_output)
            
            if self.current_step >= self.max_steps:
                self.current_step = 0
                self.state = AgentState.IDLE
                step_result = f"Terminated: Reached max steps ({self.max_steps})"
                yield (step_result, "")
        if not step_executed:
            yield ("No steps executed", "")

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
