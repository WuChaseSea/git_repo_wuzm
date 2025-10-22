# -*- coding: utf-8 -*-
import gradio as gr

from src.modules.llm import chat_llm

from src.agent.xiaoling import XIAOLING


class ChatPipeline:

    def __init__(self, demo: gr.Blocks):
        self.demo = demo

        self.register_events()

        self.xiaoling = XIAOLING(mode="知性搭子")
    
    def register_events(self):
        
        for text, btn in zip(
            ["😮‍💨 我今天有点累", "😤 有点烦同事", "😶‍🌫️ 不想工作", "💤 想摸鱼", "✍️ 说点别的（自定义输入）"],
            self.demo.mood_buttons
        ):
            btn.click(fn=lambda t=text: t, outputs=self.demo.user_input)
        
        self.demo.sbt.click(
            fn=self.chat_with_user,
            inputs=[self.demo.mode, self.demo.user_input, self.demo.chat_box],
            outputs=[self.demo.user_input, self.demo.chat_box]
        )
    
    async def chat_with_user(self, mode, user_input, chat_history):
        chat_history = list(chat_history or [])
        chat_history.append({"role": "user", "content": user_input})
        refs = ""  # 这里每一次都是空字符串会导致输出的时候只显示模型的输出，历史对话不显示，后续可以考虑加上chat_history的内容
        async for response, output in self.xiaoling.run_stream(request=user_input):
            refs += response
            yield "", [{"role": "assistant", "content": refs}]
        
        
        chat_history.append({"role": "assistant", "content": refs})

        yield "", chat_history
