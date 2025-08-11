import os
import gradio as gr
from pathlib import Path
from decouple import config
import settings
from apps.assets import PDFJS_PREBUILT_DIR, KotaemonTheme
from apps.base import BaseApp
from apps.pages import ChatPage

BASE_PATH = os.environ.get("GR_FILE_ROOT_PATH", "")


def on_upload(files):
    print("Upload called:", files)
    return "Uploading..."

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
