import gradio as gr

from apps.base import BasePage
from apps.pages.chat.control import ConversationControl
from apps.pages.chat.chat_suggestion import ChatSuggestion
from apps.pages.chat.chat_pannel import ChatPanel
from apps.files.ui import File

from models.indices.ingests.files import VP_DEFAULT_FILE_EXTRACTORS


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

                quick_upload_label = ("Quick Upload")
                with gr.Accordion(label=quick_upload_label) as _:
                    self.quick_file_upload_status = gr.Markdown()
                    self.quick_file_upload = File(
                            file_types=list(VP_DEFAULT_FILE_EXTRACTORS.keys()),
                            file_count="multiple",
                            container=True,
                            show_label=False,
                            elem_id="quick-file",
                        )
                    self.quick_urls = gr.Textbox(
                        placeholder=(
                            "Or paste URLs"
                        ),
                        lines=1,
                        container=False,
                        show_label=False,
                        elem_id=(
                            "quick-url"
                        ),
                    )
            
            with gr.Column(scale=6, elem_id="chat-area"):
                self.chat_panel = ChatPanel(self._app)
            
            with gr.Column(
                scale=4, elem_id="chat-info-panel"
            ) as self.info_column:
                with gr.Accordion(
                    label="Information panel", open=True, elem_id="info-expand"
                ):
                    self.modal = gr.HTML("<div id='pdf-modal'></div>")
                    self.plot_panel = gr.Plot(visible=False)
                    self.info_panel = gr.HTML(elem_id="html-info-panel")
            
        self.followup_questions = self.chat_suggestion.examples
        self.followup_questions_ui = self.chat_suggestion.accordion
