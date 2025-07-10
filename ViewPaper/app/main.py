import gradio as gr
from decouple import config
from app.base import BaseApp
from app.pages import ChatPage

from theflow.settings import settings as settings

KH_DEMO_MODE = getattr(settings, "KH_DEMO_MODE", False)
KH_SSO_ENABLED = getattr(settings, "KH_SSO_ENABLED", False)
KH_ENABLE_FIRST_SETUP = getattr(settings, "KH_ENABLE_FIRST_SETUP", False)
KH_APP_DATA_EXISTS = getattr(settings, "KH_APP_DATA_EXISTS", True)

# override first setup setting
if config("KH_FIRST_SETUP", default=False, cast=bool):
    KH_APP_DATA_EXISTS = False


class App(BaseApp):
    def ui(self):
        """Render the UI"""
        self._tabs = {}

        with gr.Tabs() as self.tabs:
            self.f_user_management = False
            with gr.Tab(
                    "Chat",
                    elem_id="chat-tab",
                    id="chat-tab",
                    visible=not self.f_user_management,
            ) as self._tabs["chat-tab"]:
                self.chat_page = ChatPage(self)

            if len(self.index_manager.indices) == 1:
                for index in self.index_manager.indices:
                    with gr.Tab(
                            f"{index.name}",
                            elem_id="indices-tab",
                            elem_classes=[
                                "fill-main-area-height",
                                "scrollable",
                                "indices-tab",
                            ],
                            id="indices-tab",
                            visible=not self.f_user_management and not KH_DEMO_MODE,
                    ) as self._tabs[f"{index.id}-tab"]:
                        page = index.get_index_page_ui()
                        setattr(self, f"_index_{index.id}", page)
            elif len(self.index_manager.indices) > 1:
                with gr.Tab(
                        "Files",
                        elem_id="indices-tab",
                        elem_classes=["fill-main-area-height", "scrollable", "indices-tab"],
                        id="indices-tab",
                        visible=not self.f_user_management and not KH_DEMO_MODE,
                ) as self._tabs["indices-tab"]:
                    for index in self.index_manager.indices:
                        with gr.Tab(
                                index.name,
                                elem_id=f"{index.id}-tab",
                        ) as self._tabs[f"{index.id}-tab"]:
                            page = index.get_index_page_ui()
                            setattr(self, f"_index_{index.id}", page)




