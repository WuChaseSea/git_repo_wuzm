import gradio as gr
import asyncio
import logging
from apps.logger import logger
from apps.agent.scimind import SCIMind

agent = SCIMind()

log_messages = []


def gradio_sink(message):
    log_messages.append(message.strip())


logger.add(gradio_sink, level="INFO")


async def run_async(prompt):
    async for step in agent.run_stream(prompt):
        yield step

preset_prompts= [
    "帮我总结最新的 Transformer 优化论文",
    "查询关于 LLM 在医疗领域的应用研究",
    "找一些关于图神经网络（GNN）的综述论文",
    "总结最近 arXiv 上关于 RAG 的研究进展",
]

with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 📌 常用提示词")
            prompt = gr.Textbox(label="输入你的分析意图", placeholder="例如：帮我找一些关于Transformer优化的论文...", elem_id="prompt_box")
            for text in preset_prompts:
                btn = gr.Button(text)
                # 点击时把内容填充到输入框
                btn.click(fn=lambda t=text: t, inputs=None, outputs=prompt)
        
        with gr.Column(scale=3):
            gr.Markdown("# 🧠 SCIMind | 科研论文分析Agent")
            
            output = gr.Textbox(label="结果输出", interactive=False)
            btn = gr.Button("开始分析")
            btn.click(fn=run_async, inputs=prompt, outputs=output)

if __name__ == "__main__":
    demo.launch()
