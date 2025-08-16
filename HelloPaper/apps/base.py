import os
from pathlib import Path
from abc import abstractmethod
from typing import Any, Literal, Optional, TypeVar, Iterator, AsyncGenerator

from langchain.schema.messages import AIMessage as LCAIMessage
from langchain.schema.messages import HumanMessage as LCHumanMessage
from langchain.schema.messages import SystemMessage as LCSystemMessage
from llama_index.core.bridge.pydantic import Field
from llama_index.core.schema import Document as BaseDocument

import gradio as gr
import settings
from apps.assets import PDFJS_PREBUILT_DIR, KotaemonTheme


BASE_PATH = os.environ.get("GR_FILE_ROOT_PATH", "")


class BaseApp:
    """The main app of Kotaemon

    The main application contains app-level information:
        - setting state
        - dynamic conversation state
        - user id

    Also contains registering methods for:
        - reasoning pipelines
        - indexing & retrieval pipelines

    App life-cycle:
        - Render
        - Declare public events
        - Subscribe public events
        - Register events
    """

    public_events: list[str] = []

    def __init__(self):
        self.app_name = getattr(settings, "VP_APP_NAME", "view")
        self.app_version = getattr(settings, "VP_APP_VERSION", "")
        self._theme = KotaemonTheme()

        dir_assets = Path(__file__).parent / "assets"
        with (dir_assets / "css" / "main.css").open() as fi:
            self._css = fi.read()
        with (dir_assets / "js" / "main.js").open() as fi:
            self._js = fi.read()
            self._js = self._js.replace("VP_APP_VERSION", self.app_version)
        with (dir_assets / "js" / "pdf_viewer.js").open(encoding="utf-8") as fi:
            self._pdf_view_js = fi.read()
            # workaround for Windows path
            pdf_js_dist_dir = str(PDFJS_PREBUILT_DIR).replace("\\", "\\\\")
            self._pdf_view_js = self._pdf_view_js.replace(
                "PDFJS_PREBUILT_DIR",
                pdf_js_dist_dir,
            ).replace("GR_FILE_ROOT_PATH", BASE_PATH)
        with (dir_assets / "js" / "svg-pan-zoom.min.js").open() as fi:
            self._svg_js = fi.read()

        self._favicon = str(dir_assets / "img" / "favicon.svg")

        self._callbacks: dict[str, list] = {}
        self._events: dict[str, list] = {}

    def declare_event(self, name: str):
        """Declare a public gradio event for other components to subscribe to

        Args:
            name: The name of the event
        """
        # if name in self._events:
        #     raise HookAlreadyDeclared(f"Hook {name} is already declared")
        self._events[name] = []

    def subscribe_event(self, name: str, definition: dict):
        """Register a hook for the app

        Args:
            name: The name of the hook
            hook: The hook to be registered
        """
        # if name not in self._events:
        #     raise HookNotDeclared(f"Hook {name} is not declared")
        self._events[name].append(definition)

    def get_event(self, name) -> list[dict]:
        # if name not in self._events:
        #     raise HookNotDeclared(f"Hook {name} is not declared")

        return self._events[name]

    def ui(self):
        raise NotImplementedError

    def on_subscribe_public_events(self):
        """Subscribe to the declared public event of the app"""

    def on_register_events(self):
        """Register all events to the app"""

    def _on_app_created(self):
        """Called when the app is created"""

    def make(self):
        markmap_js = """
        <script>
            window.markmap = {
                /** @type AutoLoaderOptions */
                autoLoader: {
                    toolbar: true, // Enable toolbar
                },
            };
        </script>
        """
        external_js = (
            "<script type='module' "
            "src='https://cdn.skypack.dev/pdfjs-viewer-element'>"
            "</script>"
            "<script type='module' "
            "src='https://cdnjs.cloudflare.com/ajax/libs/tributejs/5.1.3/tribute.min.js'>"  # noqa
            f"{markmap_js}"
            "<script src='https://cdn.jsdelivr.net/npm/markmap-autoloader@0.16'></script>"  # noqa
            "<script src='https://cdn.jsdelivr.net/npm/minisearch@7.1.1/dist/umd/index.min.js'></script>"  # noqa
            "</script>"
            "<link rel='stylesheet' href='https://cdnjs.cloudflare.com/ajax/libs/tributejs/5.1.3/tribute.css'/>"  # noqa
        )

        with gr.Blocks(
            theme=self._theme,
            css=self._css,
            title=self.app_name,
            analytics_enabled=False,
            js=self._js,
            head=external_js,
        ) as demo:
            self.app = demo

            self.ui()

            self.register_events()

            demo.load(None, None, None, js=self._pdf_view_js)

        return demo
    

    def register_events(self):
        """Register all events"""
        self.on_register_events()
        for value in self.__dict__.values():
            if isinstance(value, BasePage):
                value.register_events()


class BasePage:
    """The logic of the Kotaemon app"""

    public_events: list[str] = []

    def __init__(self, app):
        self._app = app

    def on_building_ui(self):
        """Build the UI of the app"""

    def on_subscribe_public_events(self):
        """Subscribe to the declared public event of the app"""

    def on_register_events(self):
        """Register all events to the app"""

    def _on_app_created(self):
        """Called when the app is created"""

    def as_gradio_component(
        self,
    ) -> Optional[gr.components.Component | list[gr.components.Component]]:
        """Return the gradio components responsible for events

        Note: in ideal scenario, this method shouldn't be necessary.
        """
        return None

    def render(self):
        for value in self.__dict__.values():
            if isinstance(value, gr.blocks.Block):
                value.render()
            if isinstance(value, BasePage):
                value.render()

    def unrender(self):
        for value in self.__dict__.values():
            if isinstance(value, gr.blocks.Block):
                value.unrender()
            if isinstance(value, BasePage):
                value.unrender()

    def declare_public_events(self):
        """Declare an event for the app"""

    def subscribe_public_events(self):
        """Subscribe to an event"""

    def register_events(self):
        """Register all events"""
        self.on_register_events()
        # for value in self.__dict__.values():
        #     if isinstance(value, BasePage):
        #         value.register_events()

    def on_app_created(self):
        """Execute on app created callbacks"""
        self._on_app_created()


IO_Type = TypeVar("IO_Type", "Document", str)
SAMPLE_TEXT = "A sample Document for HelloPaper"

class Document(BaseDocument):
    """
    Base document class, mostly inherited from Document class from llama-index.

    This class accept one positional argument `content` of an arbitrary type, which will
        store the raw content of the document. If specified, the class will use
        `content` to initialize the base llama_index class.

    Attributes:
        content: raw content of the document, can be anything
        source: id of the source of the Document. Optional.
        channel: the channel to show the document. Optional.:
            - chat: show in chat message
            - info: show in information panel
            - index: show in index panel
            - debug: show in debug panel
    """

    content: Any = None
    source: Optional[str] = None
    channel: Optional[Literal["chat", "info", "index", "debug", "plot", "info_mindmap"]] = None

    def __init__(self, content: Optional[Any] = None, *args, **kwargs):
        if content is None:
            if kwargs.get("text", None) is not None:
                kwargs["content"] = kwargs["text"]
            elif kwargs.get("embedding", None) is not None:
                kwargs["content"] = kwargs["embedding"]
                # default text indicating this document only contains embedding
                kwargs["text"] = "<EMBEDDING>"
        elif isinstance(content, Document):
            # TODO: simplify the Document class
            temp_ = content.dict()
            temp_.update(kwargs)
            kwargs = temp_
        else:
            kwargs["content"] = content
            if content:
                kwargs["text"] = str(content)
            else:
                kwargs["text"] = ""
        super().__init__(*args, **kwargs)

    def __bool__(self):
        return bool(self.content)

    @classmethod
    def example(cls) -> "Document":
        document = Document(
            text=SAMPLE_TEXT,
            metadata={"filename": "README.md", "category": "codebase"},
        )
        return document

    def __str__(self):
        return str(self.content)


class BaseComponent():
    """A component is a class that can be used to compose a pipeline.

    !!! tip "Benefits of component"
        - Auto caching, logging
        - Allow deployment

    !!! tip "For each component, the spirit is"
        - Tolerate multiple input types, e.g. str, Document, List[str], List[Document]
        - Enforce single output type. Hence, the output type of a component should be
    as generic as possible.
    """

    inflow = None

    def flow(self):
        if self.inflow is None:
            raise ValueError("No inflow provided.")

        if not isinstance(self.inflow, BaseComponent):
            raise ValueError(
                f"inflow must be a BaseComponent, found {type(self.inflow)}"
            )

        return self.__call__(self.inflow.flow())

    def set_output_queue(self, queue):
        self._queue = queue
        for name in self._ff_nodes:
            node = getattr(self, name)
            if isinstance(node, BaseComponent):
                node.set_output_queue(queue)

    def report_output(self, output: Optional[Document]):
        if self._queue is not None:
            self._queue.put_nowait(output)

    def invoke(self, *args, **kwargs) -> Document | list[Document] | None:
        ...

    async def ainvoke(self, *args, **kwargs) -> Document | list[Document] | None:
        ...

    def stream(self, *args, **kwargs) -> Iterator[Document] | None:
        ...

    def astream(self, *args, **kwargs) -> AsyncGenerator[Document, None] | None:
        ...

    @abstractmethod
    def run(
        self, *args, **kwargs
    ) -> Document | list[Document] | Iterator[Document] | None | Any:
        """Run the component."""
        ...

class BaseMessage(Document):
    def __add__(self, other: Any):
        raise NotImplementedError

    def to_openai_format(self) -> "ChatCompletionMessageParam":
        raise NotImplementedError


class SystemMessage(BaseMessage, LCSystemMessage):
    def to_openai_format(self) -> "ChatCompletionMessageParam":
        return {"role": "system", "content": self.content}


class AIMessage(BaseMessage, LCAIMessage):
    def to_openai_format(self) -> "ChatCompletionMessageParam":
        return {"role": "assistant", "content": self.content}


class HumanMessage(BaseMessage, LCHumanMessage):
    def to_openai_format(self) -> "ChatCompletionMessageParam":
        return {"role": "user", "content": self.content}


class RetrievedDocument(Document):
    """Subclass of Document with retrieval-related information

    Attributes:
        score (float): score of the document (from 0.0 to 1.0)
        retrieval_metadata (dict): metadata from the retrieval process, can be used
            by different components in a retrieved pipeline to communicate with each
            other
    """

    score: float = Field(default=0.0)
    retrieval_metadata: dict = Field(default={})


class LLMInterface(AIMessage):
    candidates: list[str] = Field(default_factory=list)
    completion_tokens: int = -1
    total_tokens: int = -1
    prompt_tokens: int = -1
    total_cost: float = 0
    logits: list[list[float]] = Field(default_factory=list)
    messages: list[AIMessage] = Field(default_factory=list)
    logprobs: list[float] = []
