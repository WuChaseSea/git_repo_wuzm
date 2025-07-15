import gradio as gr

from apps.base import BasePage
from apps.pages.chat.control import ConversationControl

class ChatPage(BasePage):
    def __init__(self, app):
        self._app = app
        self.on_building_ui()
    
    def on_building_ui(self):
        with gr.Row():
            self.state_retrieval_history = gr.State([])
            with gr.Column(scale=1, elem_id="conv-settings-panel") as self.conv_column:
                self.chat_control = ConversationControl(self._app)
                self.chat_suggestion = ChatSuggestion(self._app)
