import gradio as gr
import torch
from PIL import Image
from random import random

def build_sticker_ui(qwen_model, qwen_processor, ov_pipe):
    """
    构建“灵魂画手专属表情包”的极简交互界面。
    传入你已经加载好的三个核心组件：Qwen模型、Qwen处理器、ZImage生图管道。
    """
    
    # ==========================================
    # 核心工作流：连接 VLM 和 Image Gen
    # ==========================================
    def process_and_generate(sketch_dict, user_hint):
        # 1. 获取画板上的图 (Gradio 的 Sketchpad 会返回一个字典，composite 是最终合并的图)
        if sketch_dict is None or "composite" not in sketch_dict:
            return None, "亲，你还没有画任何东西哦！"
        
        sketch_image = sketch_dict["composite"]
        
        # 2. 调教 Qwen3-VL (充当 Prompt 翻译官)
        sys_prompt = """你是一个专业的微信表情包提示词专家。请观察这张草图，并结合用户的附加文字，将其转化为一段高质量的图像生成英文或中文提示词。
        要求包含：画面的核心主体、动作、3D盲盒质感(3D blind box style)、微信表情包风格(WeChat sticker style)、纯白背景(white background)。
        【严格警告】请只输出提示词文本本身，绝对不要包含“好的”、“为您生成”等废话。"""
        
        # 如果用户输入了附加提示（比如“我想画一只生气的猫”），就把它加上
        question = f"用户附加提示：{user_hint}。请根据草图和提示生成最终的提示词。" if user_hint else "请根据这张草图生成提示词。"

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": sketch_image},
                    {"type": "text", "text": question},
                ],
            }
        ]

        # 运行 Qwen3-VL
        inputs = qwen_processor.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_dict=True, return_tensors="pt")
        generated_ids = qwen_model.generate(**inputs, max_new_tokens=500)
        
        generated_ids_trimmed = [out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)]
        final_prompt = qwen_processor.batch_decode(generated_ids_trimmed, skip_special_tokens=True)[0]
        
        # 清理多余换行符，防报错
        final_prompt = final_prompt.replace("\n", "").strip()

        # 3. 呼叫 Z-Image 进行魔法渲染
        # 这里我们把那些复杂的参数(steps, shift)全部隐藏在代码里，不让用户操心
        negative_prompt = "丑陋, 变形, 模糊, 糟糕的解剖结构, 极简, 缺维, 乱码, 水印, 文字, 签名, 低画质, 毁容"
        
        try:
            final_image = ov_pipe(
                prompt=final_prompt,
                negative_prompt=negative_prompt,
                height=512,  # 表情包不需要 1024 那么大，512 速度更快
                width=512,
                num_inference_steps=5, # 固定一个画质和速度均衡的步数
                guidance_scale=0.0,      
                generator=torch.Generator("cpu").manual_seed(random.randint(1, 100000)), # 每次随机给个种子
            ).images[0]
            
            return final_image, final_prompt
            
        except Exception as e:
            return None, f"生成报错啦，检查一下终端输出：{str(e)}"

    # ==========================================
    # UI 界面绘制 (极简人类版)
    # ==========================================
    with gr.Blocks(title="灵魂画手表情包", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            """
            # 🎨 灵魂画手 -> 专属表情包印钞机
            只需两步：在左边随便画两笔 ➡️ 点击生成。AI 大脑会自动看懂你的梗并把它变成高清表情包！
            """
        )
        
        with gr.Row():
            # 左侧：用户输入区
            with gr.Column(scale=1):
                # 这是一个交互式画板
                canvas = gr.Sketchpad(label="第一步：在这里画下你的灵魂草图", type="pil", height=400)
                
                # 附加提示语（非必填），拯救画技太差的情况
                user_hint = gr.Textbox(label="第二步：补充一句话（可选）", placeholder="例如：这是一只趴在键盘上哭泣的猫...", lines=1)
                
                # 唯一的灵魂按钮
                submit_btn = gr.Button("🪄 施展魔法 (生成表情包)", variant="primary", size="lg")
                
            # 右侧：结果展示区
            with gr.Column(scale=1):
                output_image = gr.Image(label="为你生成的专属表情包", type="pil", height=400)
                output_prompt = gr.Textbox(label="Qwen3-VL 脑补的完整提示词 (看看它有多懂你)", interactive=False, lines=3)

        # 绑定按钮事件
        submit_btn.click(
            fn=process_and_generate,
            inputs=[canvas, user_hint],
            outputs=[output_image, output_prompt]
        )

    return demo