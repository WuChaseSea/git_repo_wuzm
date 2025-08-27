import gradio as gr
import asyncio
from apps.agent.scimind import SCIMind

agent = SCIMind()

async def process_query(prompt):
    await agent.run(prompt)
    return "✅ 任务完成，结果请查看日志或数据库（可扩展为返回文本/HTML）"

def run_async(prompt):
    return asyncio.run(process_query(prompt))

with gr.Blocks() as demo:
    gr.Markdown("# 🧠 SCIMind | 科研论文分析Agent")
    prompt = gr.Textbox(label="输入你的分析意图", placeholder="例如：帮我找一些关于Transformer优化的论文...")
    output = gr.Textbox(label="结果输出", interactive=False)
    btn = gr.Button("开始分析")
    btn.click(fn=run_async, inputs=prompt, outputs=output)

if __name__ == "__main__":
    demo.launch()
