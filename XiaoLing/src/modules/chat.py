# -*- coding: utf-8 -*-
import gradio as gr


class ChatPipeline:

    def __init__(self, demo: gr.Blocks):
        self.demo = demo

        self.register_events()
    
    def register_events(self):
        
        for text, btn in zip(
            ["😮‍💨 我今天有点累", "😤 有点烦同事", "😶‍🌫️ 不想工作", "💤 想摸鱼", "✍️ 说点别的（自定义输入）"],
            self.demo.mood_buttons
        ):
            btn.click(fn=lambda t=text: t, outputs=self.demo.user_input)
        
        self.demo.sbt.click(
            fn=self.chat_with_user,
            inputs=[self.demo.mode, self.demo.user_input, self.demo.chat_box],
            outputs=[self.demo.chat_box]
        )
    
    def chat_with_user(self, mode, user_input, chat_history):
        chat_history = list(chat_history or [])
        chat_history.append({"role": "user", "content": user_input})

        response = f"[{mode}] 小灵：{user_input}，我懂你的感觉～"
        chat_history.append({"role": "assistant", "content": response})

        return chat_history
