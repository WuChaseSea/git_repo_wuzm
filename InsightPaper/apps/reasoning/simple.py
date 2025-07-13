import logging
import threading
from textwrap import dedent
from typing import Generator
from decouple import config
from .base import BaseReasoning

logger = logging.getLogger(__name__)


DEFAULT_QA_TEXT_PROMPT = (
    "Use the following pieces of context to answer the question at the end in detail with clear explanation. "  # noqa: E501
    "If you don't know the answer, just say that you don't know, don't try to "
    "make up an answer. Give answer in "
    "{lang}.\n\n"
    "{context}\n"
    "Question: {question}\n"
    "Helpful Answer:"
)


class FullQAPipeline(BaseReasoning):
    """Question answering pipeline. Handle from question to answer"""

    class Config:
        allow_extra = True

    # configuration parameters
    trigger_context: int = 150
    use_rewrite: bool = False

    @classmethod
    def get_user_settings(cls) -> dict:

        llm = ""
        choices = [("(default)", "")]
        temp = {}
        try:
            choices += [(_, _) for _ in temp.keys()]
        except Exception as e:
            logger.exception(f"Failed to get LLM options: {e}")

        return {
            "llm": {
                "name": "Language model",
                "value": llm,
                "component": "dropdown",
                "choices": choices,
                "special_type": "llm",
                "info": (
                    "The language model to use for generating the answer. If None, "
                    "the application default language model will be used."
                ),
            },
            "highlight_citation": {
                "name": "Citation style",
                "value": (
                    "highlight"
                    if not config("USE_LOW_LLM_REQUESTS", default=False, cast=bool)
                    else "off"
                ),
                "component": "radio",
                "choices": [
                    ("citation: highlight", "highlight"),
                    ("citation: inline", "inline"),
                    ("no citation", "off"),
                ],
            },
            "create_mindmap": {
                "name": "Create Mindmap",
                "value": False,
                "component": "checkbox",
            },
            "create_citation_viz": {
                "name": "Create Embeddings Visualization",
                "value": False,
                "component": "checkbox",
            },
            "use_multimodal": {
                "name": "Use Multimodal Input",
                "value": False,
                "component": "checkbox",
            },
            "system_prompt": {
                "name": "System Prompt",
                "value": ("This is a question answering system."),
            },
            "qa_prompt": {
                "name": "QA Prompt (contains {context}, {question}, {lang})",
                "value": DEFAULT_QA_TEXT_PROMPT,
            },
            "n_last_interactions": {
                "name": "Number of interactions to include",
                "value": 5,
                "component": "number",
                "info": "The maximum number of chat interactions to include in the LLM",
            },
            "trigger_context": {
                "name": "Maximum message length for context rewriting",
                "value": 150,
                "component": "number",
                "info": (
                    "The maximum length of the message to trigger context addition. "
                    "Exceeding this length, the message will be used as is."
                ),
            },
        }

    @classmethod
    def get_info(cls) -> dict:
        return {
            "id": "simple",
            "name": "Simple QA",
            "description": (
                "Simple RAG-based question answering pipeline. This pipeline can "
                "perform both keyword search and similarity search to retrieve the "
                "context. After that it includes that context to generate the answer."
            ),
        }
