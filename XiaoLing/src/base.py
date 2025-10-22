import os
from pathlib import Path
import gradio as gr

from src.modules import ChatPipeline


class BaseApp:

    def __init__(self):
        self.app_name = "xiaoling_app"
    
    def ui(self):
        gr.Markdown("## 👋 欢迎回来，今天也要让心情发光 ✨")

        with gr.Row():
            # 第一列
            with gr.Column(scale=1, min_width=200):
                gr.Markdown("### 🎛️ 模式设置")
                self.mode = gr.Radio(["知性搭子", "可爱搭子", "吐槽搭子"], label="选择模式", value="共鸣对话", elem_id="mode_choose")

                gr.Markdown("### 🎵 音乐播放")
                self.music = gr.Audio(
                    value="assets/a-small-miracle.mp3",   # 本地音频文件路径
                    label="当前播放",
                    autoplay=False,             # 是否自动播放（True 会立即播放）
                    interactive=False           # 用户不能上传，只能播放
                )

                gr.Markdown("### 快捷情绪")
                moods = [
                    "😮‍💨 我今天有点累",
                    "😤 有点烦同事",
                    "😶‍🌫️ 不想工作",
                    "💤 想摸鱼",
                    "✍️ 说点别的（自定义输入）"
                ]
                self.mood_buttons = [gr.Button(text) for text in moods]

                gr.Markdown("### 📍 高德推荐")
                place = gr.Textbox(label="推荐地点", placeholder="例如：咖啡店 / 公园", elem_id="place_recommend")

            # 第二列和第三列内容放在一个 Column 内
            with gr.Column(scale=3, min_width=600):
                with gr.Row():
                    # 左半部分：对话区
                    with gr.Column(scale=1):
                        gr.Markdown("### 💬 小灵的共鸣对话")
                        self.chat_box = gr.Chatbot(label="与小灵聊天", type="messages", height=450, autoscroll=True)
                    # 右半部分：内容创作与广场内容
                    with gr.Column(scale=1):
                        gr.Markdown("### 🎨 内容创作")
                        self.creative_output = gr.Textbox(label="AI生成内容", placeholder="这里会出现小灵生成的文字或图像描述", lines=6)

                        gr.Markdown("### 🌈 广场相似内容")
                        square_similar = gr.Textbox(label="相似共鸣", placeholder="展示与你相似的心情与创作", lines=6)

                # 横跨两列的输入框和发送按钮
                with gr.Column(scale=3):
                    self.user_input = gr.Textbox(label="输入你的心情或想说的话", placeholder="今天的心情如何？", lines=2, elem_id="user_input")
                    self.sbt = gr.Button("发送 ✨", elem_id="send_button")

            # 第四列
            with gr.Column(scale=1, min_width=250):
                gr.Markdown("### 🧍 用户信息")
                gr.Dataframe(headers=["属性", "值"], value=[["昵称", "SoulUser001"], ["状态", "在线"], ["等级", "Lv.3"]])

                gr.Markdown("### 📈 情绪曲线")
                gr.LinePlot(
                    label="最近情绪波动",
                    x=[1, 2, 3, 4, 5],
                    y=[0.3, 0.6, 0.5, 0.8, 0.7],
                    title="情绪能量"
                )

                gr.Markdown("### 💞 潜在共鸣用户推荐")
                gr.Textbox(value="・SoulUser097（最近分享：『下班后的风真好』）\n・SoulUser112（关键词：#疲惫但不想停）", lines=5)

        # 右下角小灵成长
                gr.HTML("""
                <div style='text-align: right; margin-top: 10px;'>
                    <div style='display: inline-block; padding: 10px; border-radius: 15px; background-color: #f5f5f5; width: 300px;'>
                        <h4>🧠 小灵的成长状态</h4>
                        <p>当前等级：Lv.2 🌱</p>
                        <p>共鸣值：85/100</p>
                        <p>下一阶段：解锁「共创星球」功能 ✨</p>
                        <progress value='85' max='100' style='width: 100%; height: 10px;'></progress>
                    </div>
                </div>
                """)
    
    def make(self):
        with gr.Blocks(theme=gr.themes.Soft(), title="小灵 · 共鸣陪伴智能体") as demo:
            self.ui()

            self.chat_pipeline = ChatPipeline(self)
        
        return demo
