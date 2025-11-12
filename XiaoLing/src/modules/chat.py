# -*- coding: utf-8 -*-
import os
import gradio as gr
from datetime import datetime
import uuid

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 或者 'Microsoft YaHei'
plt.rcParams['axes.unicode_minus'] = False    # 解决坐标轴负号显示问题
import pandas as pd

from src.modules.llm import chat_llm
from src.modules.db import chat_db, content_db, emotion_db
from src.logger import logger

from src.agent.xiaoling import XIAOLING
from src.modules.amap import recommend_place


class ChatPipeline:

    def __init__(self, app, demo: gr.Blocks):
        self.app = app
        self.demo = demo

        # self.xiaoling = XIAOLING(mode="知性搭子")
        self.xiaoling = chat_llm
        self.chat_db = chat_db
        self.content_db = content_db
        self.emotion_db = emotion_db
        
        self.user_id = "0001"
        self.chat_history = self.chat_db.load_chat_records(user_id=self.user_id, limit=20)
        self.contents = self.content_db.load_content_records(user_id=self.user_id, limit=20)
        self.emotions = self.emotion_db.get_last_week_emotion(user_id=self.user_id)
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
            outputs=[self.app.user_input, self.app.chat_box, self.app.place_panel, self.app.place_panel, self.app.creative_output]
        )
    
        self.demo.load(
            fn=lambda: self.chat_history,
            outputs=[self.app.chat_box]
        )

        self.demo.load(
            fn=lambda: self.render_emotion_curve(
                self.emotion_db.get_last_week_emotion(self.user_id)
            ),
            outputs=[self.app.emotion_plot]
        )
    
    def chat_with_user(self, mode, user_input):
        self.add_history(user_id=self.user_id, mode=mode, content={"role": "user", "content": user_input}, limit=20)
        refs = ""  # 这里每一次都是空字符串会导致输出的时候只显示模型的输出，历史对话不显示，后续可以考虑加上chat_history的内容
        for response in self.xiaoling.stream(user_message={"mode": mode, "user_input": user_input}, history=self.chat_history[:10]):
            refs += response
            yield "", [{"role": "assistant", "content": refs}], "", gr.update(visible=False), ""
        
        self.add_history(user_id=self.user_id, mode=mode, content={"role": "assistant", "content": refs}, limit=20)

        yield "", self.chat_history, "", gr.update(visible=False), ""

        intention = self.xiaoling.intent_stream(user_message={"mode": mode, "user_input": user_input}, history=self.chat_history[:10])
        logger.info(f"识别到用户意图: {intention}")
        if intention == "recommend_place":
            user_amap_data = self.xiaoling.amap_recommendation(user_message={"mode": mode, "user_input": user_input}, history=self.chat_history[:10])
            places = recommend_place(emotion=user_amap_data.get("emotion"), user_location="北京", purpose=user_amap_data.get("place_type"), amap_key=os.getenv("AMAPKEY"))
            cards_html = self.recommend_place_cards(places)
            self.add_history(user_id=self.user_id, mode=mode, content={"role": "assistant", "content": "我为你推荐以下地点👇"}, limit=20)
            logger.info(f"为用户推荐了以下地点: {[p.get('name') for p in places]}")
            yield "", self.chat_history, cards_html, gr.update(visible=True), ""
        elif intention == "post_content":
            content = self.xiaoling.content_creation(user_message={"mode": mode, "user_input": user_input}, history=self.chat_history[:10])
            self.add_content(user_id=self.user_id, mode=mode, content={"role": "assistant", "content": content}, limit=20)
            yield "", self.chat_history, "", gr.update(visible=False), content
        else:
            yield "", self.chat_history, "", gr.update(visible=False), ""
        
        logger.info(f"感知用户情绪中...")
        emotion_data = self.xiaoling.emotion_score(user_message={"mode": mode, "user_input": user_input}, history=self.chat_history[:10])
        logger.info(f"识别到用户情绪: {emotion_data}")
        self.add_emotion(user_id=self.user_id, text=user_input, score=emotion_data.get("score"), emotion_label=emotion_data.get("emotion"))
    
    def recommend_place_cards(self, places):
        """把地点信息转为可显示的卡片HTML"""
        cards_html = ""
        for p in places:
            name = p.get("name", "未知地点")
            address = p.get("address", "暂无地址")
            category = p.get("type", "未知类型")
            lat = p.get("lat")
            lng = p.get("lng")
            # 构建高德导航链接（lng,lat 必须都有）
            if lat and lng:
                nav_url = f"https://uri.amap.com/navigation?to={lng},{lat},{name}&mode=car&src=gradio"
            else:
                nav_url = "#"
            card = f"""
                <div style="padding:14px; border-radius:12px; border:1px solid #eee; margin-bottom:10px;">
                    
                    <!-- 顶部一行，名称 + 按钮 -->
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <div style="font-size:18px; font-weight:600;">{name}</div>
                        <a href="{nav_url}" target="_blank"
                        style="padding:6px 12px; background:#0078ff; color:white; 
                                border-radius:8px; text-decoration:none; font-size:14px;">
                            去这儿 🚗
                        </a>
                    </div>

                    <div style="color:#666; margin-bottom:4px;">📍 {address}</div>
                    <div style="color:#999;">🏷️ {category}</div>
                </div>
                """
            cards_html += card
        return cards_html
    
    def render_emotion_curve(self, emotion_data):
        """
        emotion_data: List[(timestamp, score)]
        Example: [("2025-02-01", 0.3), ("2025-02-02", 0.6), ...]
        """

        if not emotion_data:
            fig, ax = plt.subplots(figsize=(5, 2.5))
            ax.text(0.5, 0.5, "暂无情绪记录", ha='center', va='center')
            ax.axis("off")
            return fig

        df = pd.DataFrame(emotion_data, columns=["timestamp", "score"])
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        fig, ax = plt.subplots(figsize=(5, 2.5))
        ax.plot(df["timestamp"], df["score"], linewidth=2, marker='o')

        ax.set_ylim(-1, 1)
        ax.set_title("最近 7 天情绪波动", fontsize=12, pad=10)
        ax.set_xlabel("")
        ax.set_ylabel("情绪能量（-1 ~ +1）")

        # 设置横轴时间格式
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=5))  # 最多显示5个刻度
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')  # 倾斜标签，避免重叠

        # 柔和样式
        ax.grid(alpha=0.3)

        return fig

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
    
    def add_content(self, user_id="0", mode="知性搭子", content={"role": "assistant", "content": None}, limit=20):
        role = content.get("role")
        content = content.get("content")
        self.content_db.save_content_record(
            user_id=user_id,
            mode=mode,
            role=role,
            content=content,
            emotion="正常",
            session_id=self.chat_session_id
        )
        self.contents = self.content_db.load_content_records(user_id=user_id, limit=limit)
    
    def add_emotion(self, user_id="0", text="", score=0.0, emotion_label="正常"):
        self.emotion_db.save_emotion_record(
            user_id=user_id,
            text=text,
            score=score,
            emotion_label=emotion_label
        )
        self.emotions = self.emotion_db.get_last_week_emotion(user_id=self.user_id)
