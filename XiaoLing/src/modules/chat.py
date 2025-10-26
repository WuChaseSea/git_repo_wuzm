# -*- coding: utf-8 -*-
import gradio as gr
from datetime import datetime
import uuid

from src.modules.llm import chat_llm
from src.modules.db import chat_db

from src.agent.xiaoling import XIAOLING


class ChatPipeline:

    def __init__(self, app, demo: gr.Blocks):
        self.app = app
        self.demo = demo

        # self.xiaoling = XIAOLING(mode="知性搭子")
        self.xiaoling = chat_llm
        self.chat_db = chat_db
        
        self.user_id = "0001"
        self.chat_history = self.chat_db.load_chat_records(user_id=self.user_id, limit=20)
        self.chat_session_id = f"{self.user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    
        self.register_events()

    def register_events(self):
        
        if len(self.chat_history) == 0:
            for text, btn in zip(
                ["😮‍💨 我今天有点累", "😤 有点烦同事", "😶‍🌫️ 不想工作", "💤 想摸鱼", "✍️ 说点别的（自定义输入）"],
                self.app.mood_buttons
            ):
                btn.click(fn=lambda t=text: t, outputs=self.app.user_input)
        else:
            mode = self.app.mode.value if self.app.mode.value else "知性搭子"
            texts = self.xiaoling.provided_chat(mode=mode, history=self.chat_history[:10])
            for text, btn in zip(
                texts,
                self.app.mood_buttons
            ):
                btn.value = text
                btn.click(fn=lambda t=text: t, outputs=self.app.user_input)
        
        self.app.sbt.click(
            fn=self.chat_with_user,
            inputs=[self.app.mode, self.app.user_input],
            outputs=[self.app.user_input, self.app.chat_box]
        )
    
        self.demo.load(
            fn=lambda: self.chat_history,
            outputs=[self.app.chat_box]
        )
    
    def chat_with_user(self, mode, user_input):
        self.add_history(user_id=self.user_id, mode=mode, content={"role": "user", "content": user_input}, limit=20)
        refs = ""  # 这里每一次都是空字符串会导致输出的时候只显示模型的输出，历史对话不显示，后续可以考虑加上chat_history的内容
        for response in self.xiaoling.stream(user_message={"mode": mode, "user_input": user_input}, history=self.chat_history[:10]):
            refs += response
            yield "", [{"role": "assistant", "content": refs}]
        
        self.add_history(user_id=self.user_id, mode=mode, content={"role": "assistant", "content": refs}, limit=20)

        yield "", self.chat_history

        intention = self.xiaoling.intent_stream(user_message={"mode": mode, "user_input": user_input}, history=self.chat_history[:10])

    
    def add_history(self, user_id="0", mode="知性搭子", content={"role": "user", "content": None}, limit=20):
        user_input = content.get("content") if content.get("role") == "user" else ""
        bot_reply = content.get("content") if content.get("role") == "assistant" else ""
        self.chat_db.save_chat_record(
            user_id=user_id,
            mode=mode,
            role=content.get("role"),
            user_input=user_input,
            bot_reply=bot_reply,
            emotion="正常",
            session_id=self.chat_session_id
        )
        self.chat_history = self.chat_db.load_chat_records(user_id=user_id, limit=limit)
