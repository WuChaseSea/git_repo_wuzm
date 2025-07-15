import gradio as gr
from decouple import config
from apps.base import BaseApp
from apps.pages import ChatPage

class App(BaseApp):
    def ui(self):
        """Render the UI"""
        self._tabs = {}

        with gr.Tabs() as self.tabs:
            # self.f_user_management = False
            with gr.Tab(
                    "Chat",
                    elem_id="chat-tab",
                    id="chat-tab",
                    visible=True,
            ) as self._tabs["chat-tab"]:
                self.chat_page = ChatPage(self)  # 主聊天界面构建
                # pass
            