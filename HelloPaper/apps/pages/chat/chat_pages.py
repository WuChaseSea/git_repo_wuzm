import gradio as gr
from pathlib import Path

from apps.base import BasePage
from apps.pages.chat.control import ConversationControl
from apps.pages.chat.chat_suggestion import ChatSuggestion
from apps.pages.chat.chat_pannel import ChatPanel
from apps.files.ui import File

from models.indices.ingests.files import VP_DEFAULT_FILE_EXTRACTORS


class ChatPage(BasePage):
    def __init__(self, app):
        self._app = app
        self._indices_input = []
        self._indices_input.append(0)
        self.on_building_ui()
        self.register_already = False
    
    def on_building_ui(self):
        with gr.Row():
            self.state_retrieval_history = gr.State([])
            with gr.Column(scale=1, elem_id="conv-settings-panel") as self.conv_column:
                self.chat_control = ConversationControl(self._app)
                self.chat_suggestion = ChatSuggestion(self._app)

                quick_upload_label = ("Quick Upload")
                with gr.Accordion(label=quick_upload_label) as _:
                    self.quick_file_upload_status = gr.Markdown("none")
                    self.quick_file_upload = gr.File(
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

    
    def on_upload(self, files):
        print("Upload called:", files)
        return "Uploading..."
    
    def on_register_quick_uploads(self):
        if not self.register_already:
            print(f"begin register quick uploads")
            quickUploadedEvent = self._app.chat_page.quick_file_upload.upload(
                fn=lambda: gr.update(
                    value="Please wait for the indexing process "
                    "to complete before adding your question."
                ),
                outputs=self._app.chat_page.quick_file_upload_status,
            )
            quickUploadedEvent.then(
                fn=self.index_fn_file_with_default_loaders,
                inputs=[
                    self.quick_file_upload,
                    gr.State(value=False)
                ],
                outputs=self.quick_file_upload_status,
                concurrency_limit=10,
            )
            quickUploadedEvent.success(
                fn=lambda: gr.update(
                    value="Please wait for the indexing process to complete before adding your question."
                ),
                outputs=self.quick_file_upload_status,
            )
            self.quickUploadedEvent = quickUploadedEvent  # 保持引用
            self.register_already = True
            return quickUploadedEvent
    
    def on_register_events(self):
        print(f"register events...")
        self.on_register_quick_uploads()
    
    def index_fn_file_with_default_loaders(
        self, files, reindex: bool
    ) -> list["str"]:
        """Function for quick upload with default loaders

        Args:
            files: the list of files to be uploaded
            reindex: whether to reindex the files
            selected_files: the list of files already selected
            settings: the settings of the app
        """
        print("Overriding with default loaders")
        import ipdb;ipdb.set_trace()
