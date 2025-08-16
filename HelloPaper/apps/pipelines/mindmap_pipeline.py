import logging
from textwrap import dedent
from theflow import Node

from llama_index.core import PromptTemplate

from apps.base import BaseComponent, Document, HumanMessage, SystemMessage

logger = logging.getLogger(__name__)


MINDMAP_HTML_EXPORT_TEMPLATE = dedent(
    """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Mindmap</title>
    <style>
      svg.markmap {
        width: 100%;
        height: 100vh;
      }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/markmap-autoloader@0.16"></script>
  </head>
  <body>
    {markmap_div}
  </body>
</html>
"""
)


class MindmapPipeline(BaseComponent):
    """Create a mindmap from the question and context"""

    SYSTEM_PROMPT = """
From now on you will behave as "MapGPT" and, for every text the user will submit, you are going to create a PlantUML mind map file for the inputted text to best describe main ideas. Format it as a code and remember that the mind map should be in the same language as the inputted context. You don't have to provide a general example for the mind map format before the user inputs the text.
    """  # noqa: E501
    MINDMAP_PROMPT_TEMPLATE = """
Question:
{question}

Context:
{context}

Generate a sample PlantUML mindmap for based on the provided question and context above. Only includes context relevant to the question to produce the mindmap.

Use the template like this:

@startmindmap
* Title
** Item A
*** Item B
**** Item C
*** Item D
@endmindmap
    """  # noqa: E501
    prompt_template: str = MINDMAP_PROMPT_TEMPLATE

    def __init__(self, llm):
        self.llm = llm

    @classmethod
    def convert_uml_to_markdown(cls, text: str) -> str:
        start_phrase = "@startmindmap"
        end_phrase = "@endmindmap"

        try:
            text = text.split(start_phrase)[-1]
            text = text.split(end_phrase)[0]
            text = text.strip().replace("*", "#")
        except IndexError:
            text = ""

        return text

    def run(self, question: str, context: str) -> Document:  # type: ignore
        prompt_template = PromptTemplate(self.prompt_template)
        prompt = prompt_template.format(
            question=question,
            context=context,
        )
        messages = [
            {
                "role": "system",
                "content": self.SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        responses = {}
        for responses in self.llm.chat(messages=messages):
            pass
        uml_text = responses[0]["content"]
        markdown_text = self.convert_uml_to_markdown(uml_text)

        return Document(
            text=markdown_text,
        )
