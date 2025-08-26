import os
import gradio as gr
from pathlib import Path
from textwrap import dedent
from plotly.io import from_json
import arxiv

import settings

from apps.base import BasePage, Document
from apps.pages.chat.control import ConversationControl
from apps.pages.chat.chat_suggestion import ChatSuggestion
from apps.pages.chat.chat_pannel import ChatPanel
from apps.files.ui import File
from apps.pipelines import FilePipeline, LLMPipeline, ArxivPipeline
from apps.reasoning import FullQAPipeline

from .utils import download_arxiv_pdf, is_arxiv_url

from models.indices.ingests.files import VP_DEFAULT_FILE_EXTRACTORS

DEFAULT_QUESTION = (
    "What is the summary of this paper?"
)

chat_input_focus_js = """
function() {
    let chatInput = document.querySelector("#chat-input textarea");
    chatInput.focus();
}
"""

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

pdfview_js = """
function() {
    setTimeout(fullTextSearch(), 100);

    // Get all links and attach click event
    var links = document.getElementsByClassName("pdf-link");
    for (var i = 0; i < links.length; i++) {
        links[i].onclick = openModal;
    }

    // Get all citation links and attach click event
    var links = document.querySelectorAll("a.citation");
    for (var i = 0; i < links.length; i++) {
        links[i].onclick = scrollToCitation;
    }

    var markmap_div = document.querySelector("div.markmap");
    var mindmap_el_script = document.querySelector('div.markmap script');

    if (mindmap_el_script) {
        markmap_div_html = markmap_div.outerHTML;
    }

    // render the mindmap if the script tag is present
    if (mindmap_el_script) {
        markmap.autoLoader.renderAll();
    }

    setTimeout(() => {
        var mindmap_el = document.querySelector('svg.markmap');

        var text_nodes = document.querySelectorAll("svg.markmap div");
        for (var i = 0; i < text_nodes.length; i++) {
            text_nodes[i].onclick = fillChatInput;
        }

        if (mindmap_el) {
            function on_svg_export(event) {
                html = "{html_template}";
                html = html.replace("{markmap_div}", markmap_div_html);
                spawnDocument(html, {window: "width=1000,height=1000"});
            }

            var link = document.getElementById("mindmap-toggle");
            if (link) {
                link.onclick = function(event) {
                    event.preventDefault(); // Prevent the default link behavior
                    var div = document.querySelector("div.markmap");
                    if (div) {
                        var currentHeight = div.style.height;
                        if (currentHeight === '400px' || (currentHeight === '')) {
                            div.style.height = '650px';
                        } else {
                            div.style.height = '400px'
                        }
                    }
                };
            }

            if (markmap_div_html) {
                var link = document.getElementById("mindmap-export");
                if (link) {
                    link.addEventListener('click', on_svg_export);
                }
            }
        }
    }, 250);

    return [links.length]
}
""".replace(
    "{html_template}",
    MINDMAP_HTML_EXPORT_TEMPLATE.replace("\n", "").replace('"', '\\"'),
)

chat_input_focus_js_with_submit = """
function() {
    let chatInput = document.querySelector("#chat-input textarea");
    let chatInputSubmit = document.querySelector("#chat-input button.submit-button");
    chatInputSubmit.click();
    chatInput.focus();
}
"""


class ChatPage(BasePage):
    def __init__(self, app):
        self._app = app
        self._indices_input = []
        self._indices_input.append(0)
        self.on_building_ui()

        self._preview_links = gr.State(value=None)
        self._use_suggestion = gr.State(
            value=getattr(settings, "VP_FEATURE_CHAT_SUGGESTION", False)
        )
    
    def on_building_ui(self):
        with gr.Row():
            self.state_retrieval_history = gr.State([])
            with gr.Column(scale=1, elem_id="conv-settings-panel") as self.conv_column:
                self.chat_control = ConversationControl(self._app)
                self.chat_suggestion = ChatSuggestion(self._app)

                quick_upload_label = ("Quick Upload")
                with gr.Accordion(label=quick_upload_label) as _:
                    self.quick_file_upload_status = gr.Markdown()
                    self.quick_file_upload = gr.File(
                            file_types=list(VP_DEFAULT_FILE_EXTRACTORS.keys()),
                            file_count="multiple",
                            container=True,
                            show_label=False,
                            elem_id="quick-file",
                        )
                    
                    self.quick_urls = gr.Textbox(
                        placeholder=(
                            "Paste Arxiv URLs\n(https://arxiv.org/abs/xxx)"
                        ),
                        lines=1,
                        container=False,
                        show_label=False,
                        elem_id=(
                            "quick-url"
                        ),
                    )
                
                with gr.Blocks() as _:
                    with gr.Row():
                        self.predefined_interested_categories = gr.CheckboxGroup(
                            choices = [
                                "RAG", "Agent", "Foundation Model"
                            ],
                            label="选择感兴趣类别（可多选）"
                        )
                    with gr.Row():
                        self.user_add_interested_categories = gr.Textbox(
                            placeholder="输入自定义感兴趣类型，多个用逗号分隔",
                            label="自定义感兴趣类别"
                        )
                    with gr.Row():
                        self.arxiv_max_results = gr.Slider(
                            minimum=1, maximum=20, step=1, value=5,
                            label="查询数量 (Max Results)",
                            interactive=True
                        )
                        self.arxiv_search_btn = gr.Button("Arxiv查询检索")
            
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
    
    def on_register_events(self):
        print(f"register events...")
        self.on_register_quick_uploads()
        self.on_register_chat_event()

        def toggle_chat_suggestion(current_state):
            return current_state, gr.update(visible=current_state)
        
        def raise_error_on_state(state):
            if not state:
                raise ValueError("Chat suggestion disabled")
            
        
        onSuggestChatEvent = {
            "fn": self.suggest_chat_conv,
            "inputs": [
                self.chat_panel.chatbot,
                self._use_suggestion
            ],
            "outputs": [
                self.followup_questions_ui,
                self.followup_questions
            ],
            "show_progress": "hidden"
        }
        self.chat_control.cb_suggest_chat.change(
            fn=toggle_chat_suggestion,
            inputs=[self.chat_control.cb_suggest_chat],
            outputs=[self._use_suggestion, self.followup_questions_ui],
            show_progress="hidden"
        ).then(
            fn=raise_error_on_state,
            inputs=[self._use_suggestion],
            show_progress="hidden"
        ).success(
            **onSuggestChatEvent
        )

        self.followup_questions.select(
            self.chat_suggestion.select_example,
            outputs=[self.chat_panel.text_input],
            show_progress="hidden",
        ).then(
            fn=None,
            inputs=None,
            outputs=None,
            js=chat_input_focus_js,
        )

        self.arxiv_search_btn.click(
            fn=self.search_arxiv_papers,
            inputs=[
                self.predefined_interested_categories,
                self.user_add_interested_categories,
                self.arxiv_max_results,
                self.chat_panel.chatbot
            ],
            outputs=[
                self.chat_panel.chatbot,
                self.info_panel,
                self.plot_panel
            ],
            concurrency_limit=20,
            show_progress="minimal"
        )
    
    def on_upload(self, files):
        print("Upload called:", files)
        return "Uploading..."
    
    def on_register_quick_uploads(self):
        quickUploadedEvent = (
            self._app.chat_page.quick_file_upload.upload(
                fn=lambda: gr.update(
                    value="Please wait for the indexing process "
                    "to complete before adding your question."
                ),
                outputs=self._app.chat_page.quick_file_upload_status,
            )
            .then(
                fn=self.index_fn_file_with_default_loaders,
                inputs=[
                    self.quick_file_upload,
                    gr.State(value=False)
                ],
                outputs=self._app.chat_page.quick_file_upload_status,
                concurrency_limit=10,
            )
            .success(
                fn=lambda: gr.update(
                    value=None
                ),
                outputs=self._app.chat_page.quick_file_upload,
            )
        )
        quickUploadedEvent = (
            quickUploadedEvent.success(
                fn=lambda: gr.update(value="Indexing completed."),
                outputs=self._app.chat_page.quick_file_upload_status,
            )
            .then(
                fn=lambda: True,
                inputs=None,
                outputs=None,
                js=chat_input_focus_js_with_submit,
            )
            .success(
                fn=lambda: gr.update(value=None),
                outputs=self._app.chat_page.quick_urls,
            )
        )

        quickURLUploadedEvent = (
            self._app.chat_page.quick_urls.submit(
                fn=lambda: gr.update(
                    value="Please wait for the indexing process "
                    "to complete before adding your question."
                ),
                outputs=self._app.chat_page.quick_file_upload_status,
            )
            .then(
                fn=self.index_fn_url_with_default_loaders,
                inputs=self.quick_urls,
                outputs=self._app.chat_page.quick_file_upload_status,
                concurrency_limit=10,
            )
        )
    
    def on_register_chat_event(self):
        chat_event = (
            gr.on(
                triggers=[self.chat_panel.text_input.submit],
                fn =self.submit_msg,
                inputs=[
                    self.chat_panel.text_input,
                    self.chat_panel.chatbot,
                ],
                outputs=[
                    self.chat_panel.text_input,
                    self.chat_panel.chatbot
                ],
                concurrency_limit=20,
                show_progress="hidden"
            )
            .success(
                fn=self.chat_fn,
                inputs=[
                    self.chat_panel.chatbot
                ],
                outputs=[
                    self.chat_panel.chatbot,
                    self.info_panel,
                    self.plot_panel
                ],
                concurrency_limit=20,
                show_progress="minimal"
            )
            .then(
                fn=lambda: True,
                inputs=None,
                outputs=[self._preview_links],
                js=pdfview_js
            )
        )
        onSuggestChatEvent = {
            "fn": self.suggest_chat_conv,
            "inputs": [
                self.chat_panel.chatbot,
                self._use_suggestion
            ],
            "outputs": [
                self.followup_questions_ui,
                self.followup_questions
            ],
            "show_progress": "hidden"
        }
        chat_event = chat_event.success(**onSuggestChatEvent)
    
    def _json_to_plot(self, json_dict: dict | None):
        if json_dict:
            plot = from_json(json_dict)
            plot = gr.update(visible=True, value=plot)
        else:
            plot = gr.update(visible=False)
        return plot
    
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
        self.file_pipeline = FilePipeline(files[0])
        self.llm_pipeline = LLMPipeline()
    
    def index_fn_url_with_default_loaders(self, url):
        if not is_arxiv_url(url):
            raise ValueError("All URLs must be valid arXiv URLs")
        print(f"get valid url: {url}")
        output_file = download_arxiv_pdf(url, output_path=os.environ.get("GRADIO_TEMP_DIR", "/tmp"))
        print(f"pdf had been saved to {output_file}")
        
        self.file_pipeline = FilePipeline(output_file)
        self.llm_pipeline = LLMPipeline()
    
    def submit_msg(
        self,
        chat_input, 
        chat_history
    ):
        if not chat_input:
            raise ValueError("Input is empty")
        
        chat_input_text = chat_input.get("text", "")
        if not chat_input_text:
            chat_input_text = DEFAULT_QUESTION
        if chat_input_text:
            chat_history = chat_history + [(chat_input_text, None)]
        else:
            if not chat_history:
                raise gr.Error("Empty chat")
        
        return ([{}, chat_history])
        
    def chat_fn(
        self,
        chat_history,
    ):
        chat_input, chat_output = chat_history[-1]
        chat_history =chat_history[:-1]

        qa_pipeline = FullQAPipeline(self.file_pipeline, self.llm_pipeline)

        text, refs, plot, plot_gr = "", "", None, gr.update(visible=False)
        msg_placeholder = "Thinking..."
        yield (
            chat_history + [(chat_input, text or msg_placeholder)],
            refs,
            plot_gr
        )
        
        try:
            for response in qa_pipeline.stream(message=chat_input, history=chat_history):
                if not isinstance(response, Document):
                    continue
                if response.channel is None:
                    continue
                if response.channel == "chat":
                    if response.content is None:
                        text = ""
                    else:
                        text += response.content
                if response.channel == "info":
                    if response.content is None:
                        refs = ""
                    else:
                        refs += response.content
                if response.channel == "plot":
                    plot = response.content
                    plot_gr = self._json_to_plot(plot)
                if response.channel == "info_mindmap":
                    if response.content is None:
                        refs = ""
                    else:
                        refs = response.content + refs
                
                yield (
                    chat_history + [(chat_input, text or msg_placeholder)],
                    refs,
                    plot_gr
                )
        except ValueError as e:
            print(e)
        
        if not text:
            empty_msg = "Sorry, I don't know."
            print(f"Generate nothing: {empty_msg}")
            yield (
                chat_history + [(chat_input, text or empty_msg)],
                refs,
                plot_gr
            )
    
    def suggest_chat_conv(
        self,
        chat_history,
        use_suggestion
    ):
        if use_suggestion:
            return gr.update(visible=True), gr.update()

        return gr.update(visible=False), gr.update()
    
    def search_arxiv_papers(
        self,
        predefined_categories,
        user_added_categories,
        max_results,
        chat_history
    ):
        self.arxiv_pipeline = ArxivPipeline()
        selected_categories = predefined_categories or []
        if user_added_categories.strip():
            selected_categories += [kw.strip() for kw in user_added_categories.split(",")]
        formatted_query = " AND ".join(f'all:"{kw.strip()}"' for kw in selected_categories)
        chat_output = f"构建的arxiv查询关键词是：{formatted_query}"
        print(chat_output)
        chat_input = "Search recent papers."
        chat_history.append((chat_input, chat_output))

        text, refs, plot, plot_gr = "", "", None, gr.update(visible=False)
        yield (
            [(chat_input, chat_output)],
            refs,
            plot_gr
        )
        
        try:
            for response in self.arxiv_pipeline.stream(formatted_query, max_results):
                if not isinstance(response, Document):
                    continue
                if response.channel is None:
                    continue
                if response.channel == "chat":
                    if response.content is None:
                        text = ""
                    else:
                        text += response.content
                if response.channel == "info":
                    if response.content is None:
                        refs = ""
                    else:
                        refs += response.content
                
                yield (
                    chat_history + [(None, text)],
                    refs,
                    plot_gr
                )

        except ValueError as e:
            print(e)

