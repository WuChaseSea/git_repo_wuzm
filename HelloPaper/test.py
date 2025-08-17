import gradio as gr

# 预置选项
preset_options = [
    "Large Language Model",
    "RAG",
    "Reinforcement Learning",
    "World Models",
    "Multi-Agent Systems"
]

def combine_inputs(predefined, custom):
    # 合并用户选择和自定义输入
    selected = predefined or []
    if custom.strip():
        selected += [kw.strip() for kw in custom.split(",")]
    return f"你选择的类型: {', '.join(selected)}"

with gr.Blocks() as demo:
    with gr.Row():
        predefined = gr.CheckboxGroup(
            choices=preset_options,
            label="请选择你感兴趣的类型（可多选）"
        )
        custom = gr.Textbox(
            placeholder="输入自定义类型，多个用逗号分隔",
            label="自定义类型"
        )
    output = gr.Textbox(label="合并结果")

    btn = gr.Button("提交")
    btn.click(fn=combine_inputs, inputs=[predefined, custom], outputs=output)

demo.launch()
