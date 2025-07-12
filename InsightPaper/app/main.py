import gradio as gr
from decouple import config
from app.base import BaseApp
from app.pages import ChatPage
from app.pages.setup import SetupPage
import settings
# from theflow.settings import settings as settings

VP_DEMO_MODE = getattr(settings, "VP_DEMO_MODE", False)  # 是否是演示模式，应该是False
VP_ENABLE_FIRST_SETUP = getattr(settings, "VP_ENABLE_FIRST_SETUP", False)  # 是否是第一次设置，True
VP_APP_DATA_EXISTS = getattr(settings, "VP_APP_DATA_EXISTS", True)  # APP数据目录是否存在

# override first setup setting
if config("VP_FIRST_SETUP", default=False, cast=bool):
    VP_APP_DATA_EXISTS = False

def toggle_first_setup_visibility():
    global VP_APP_DATA_EXISTS
    is_first_setup = not VP_DEMO_MODE and not VP_APP_DATA_EXISTS
    VP_APP_DATA_EXISTS = True
    return gr.update(visible=is_first_setup), gr.update(visible=not is_first_setup)


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
                    visible=not self.f_user_management,
            ) as self._tabs["chat-tab"]:
                self.chat_page = ChatPage(self)  # 主聊天界面构建
            
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
                        visible=not self.f_user_management and not VP_DEMO_MODE,
                    ) as self._tabs[f"{index.id}-tab"]:
                        page = index.get_index_page_ui()
                        setattr(self, f"_index_{index.id}", page)
            
            if VP_ENABLE_FIRST_SETUP:
                with gr.Column(visible=False) as self.setup_page_wrapper:
                    self.setup_page = SetupPage(self)
    
    def on_subscribe_public_events(self):
        from app.db.engine import engine
        from app.db.models import User
        from sqlmodel import Session, select

        def toggle_login_visibility(user_id):
            if not user_id:
                return list(
                    (
                        gr.update(visible=True)
                        if k == "login-tab"
                        else gr.update(visible=False)
                    )
                    for k in self._tabs.keys()
                ) + [gr.update(selected="login-tab")]

            with Session(engine) as session:
                user = session.exec(select(User).where(User.id == user_id)).first()
                if user is None:
                    return list(
                        (
                            gr.update(visible=True)
                            if k == "login-tab"
                            else gr.update(visible=False)
                        )
                        for k in self._tabs.keys()
                    )

                is_admin = user.admin

            tabs_update = []
            for k in self._tabs.keys():
                if k == "login-tab":
                    tabs_update.append(gr.update(visible=False))
                elif k == "resources-tab":
                    tabs_update.append(gr.update(visible=is_admin))
                else:
                    tabs_update.append(gr.update(visible=True))

            tabs_update.append(gr.update(selected="chat-tab"))

            return tabs_update

        # self.subscribe_event(
        #     name="onSignIn",
        #     definition={
        #         "fn": toggle_login_visibility,
        #         "inputs": [self.user_id],
        #         "outputs": list(self._tabs.values()) + [self.tabs],
        #         "show_progress": "hidden",
        #     },
        # )

        # self.subscribe_event(
        #     name="onSignOut",
        #     definition={
        #         "fn": toggle_login_visibility,
        #         "inputs": [self.user_id],
        #         "outputs": list(self._tabs.values()) + [self.tabs],
        #         "show_progress": "hidden",
        #     },
        # )

    def _on_app_created(self):
        """Called when the app is created"""

        if VP_ENABLE_FIRST_SETUP:
            self.app.load(
                toggle_first_setup_visibility,
                inputs=[],
                outputs=[self.setup_page_wrapper, self.tabs],
            )
