import gradio as gr

from apps.base import BasePage

ASSETS_DIR = "apps/assets/icons"

class ConversationControl(BasePage):
    def __init__(self, app):
        self._app = app

        self.on_building_ui()
    
    def on_building_ui(self):
        with gr.Row():
            title_text = "Conversations"
            gr.Markdown("## {}".format(title_text))
            # 黑暗模式切换
            self.btn_toggle_dark_mode = gr.Button(
                value="",
                icon=f"{ASSETS_DIR}/dark_mode.svg",
                scale=1,
                size="sm",
                elem_classes=["no-background", "body-text-color"],
                elem_id="toggle-dark-button",
            )
            # 聊天扩展按钮
            self.btn_chat_expand = gr.Button(
                value="",
                icon=f"{ASSETS_DIR}/expand.svg",
                scale=1,
                size="sm",
                elem_classes=["no-background", "body-text-color"],
                elem_id="chat-expand-button",
            )
            # pannel扩展按钮
            self.btn_info_expand = gr.Button(
                value="",
                icon=f"{ASSETS_DIR}/expand.svg",
                min_width=2,
                scale=1,
                size="sm",
                elem_classes=["no-background", "body-text-color"],
                elem_id="info-expand-button",
            )

            self.btn_toggle_dark_mode.click(
                None,
                js="""
                () => {
                    document.body.classList.toggle('dark');
                }
                """,
            )
        # 聊天 conversation选择界面
        self.conversation_id = gr.State(value="")
        self.conversation = gr.Dropdown(
            label="Chat sessions",
            choices=[],
            container=False,
            filterable=True,
            interactive=True,
            elem_classes=["unset-overflow"],
            elem_id="conversation-dropdown",
        )
        with gr.Row() as self._new_delete:
            # 是否使用 conversation suggestion
            self.cb_suggest_chat = gr.Checkbox(
                value=False,
                label="Suggest chat",
                min_width=10,
                scale=6,
                elem_id="suggest-chat-checkbox",
                container=False,
                visible=True,
            )
            # 重命名按钮
            self.btn_conversation_rn = gr.Button(
                value="",
                icon=f"{ASSETS_DIR}/rename.svg",
                min_width=2,
                scale=1,
                size="sm",
                elem_classes=["no-background", "body-text-color"],
            )
            # 删除对话按钮
            self.btn_del = gr.Button(
                value="",
                icon=f"{ASSETS_DIR}/delete.svg",
                min_width=2,
                scale=1,
                size="sm",
                elem_classes=["no-background", "body-text-color"],
            )
            # 新建对话按钮
            self.btn_new = gr.Button(
                value="",
                icon=f"{ASSETS_DIR}/new.svg",
                min_width=2,
                scale=1,
                size="sm",
                elem_classes=["no-background", "body-text-color"],
                elem_id="new-conv-button",
            )
        # 为什么这里写个不可见呢
        with gr.Row(visible=False) as self._delete_confirm:
            self.btn_del_conf = gr.Button(
                value="Delete",
                variant="stop",
                min_width=10,
            )
            self.btn_del_cnl = gr.Button(value="Cancel", min_width=10)
