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
