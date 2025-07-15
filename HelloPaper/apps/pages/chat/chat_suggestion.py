import gradio as gr

from apps.base import BasePage

class ChatSuggestion(BasePage):
    CHAT_SAMPLES = [
            "Summary this document",
            "Generate a FAQ for this document",
            "Identify the main highlights in bullet points",
        ]
    def __init__(self, app):
        self._app = app
        self.on_building_ui()
    
    def on_building_ui(self):
        self.chat_samples = [[each] for each in self.CHAT_SAMPLES]
        with gr.Accordion(
            label="Chat Suggestion",
            visible=True,
        ) as self.accordion:
            self.default_example = gr.State(
                value=self.chat_samples,
            )
            self.examples = gr.DataFrame(
                value=self.chat_samples,
                headers=["Next Question"],
                interactive=False,
                elem_id="chat-suggestion",
                wrap=True,
            )
