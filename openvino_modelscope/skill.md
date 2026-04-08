---
name: multimodal_image_studio
description: "当主要输入或输出涉及图像生成、图像编辑或图像风格迁移时，随时使用此技能。这意味着适用于用户希望执行以下操作的任何任务：根据简短文本描述或粗略草图生成新图像；对现有照片进行语义编辑（例如，添加对象、更改表情、修改背景）；或将参考图像的艺术风格迁移到内容图像上。特别是当用户提及绘制、生成、重塑或编辑视觉内容时触发——即使是随口提及（比如“把这家伙变黄”或“把我的照片变成3D盲盒”）。交付成果必须是图像文件。当主要交付成果是纯文本分析、文档创建或纯数据处理时，请勿触发此技能。"
license: Proprietary. 完整的条款见 LICENSE.txt
metadata: { "builtin_skill_version": "1.0", "engine": "OpenVINO", "vlm": "Qwen3-VL", "diffusion": "Z-Image" }
---

> **重要提示：** > 本技能需要通过 Python 执行器运行本地模型。
> 如果本地不存在独立的脚本文件，请**直接使用你的 Python 代码执行工具（如 `execute_python_code` 或类似工具）提取并运行本文档底部的【完整执行脚本】**。

# 输出要求 (Requirements for Outputs)

## 所有生成的图像

### 视觉质量与约束
- **分辨率**：除非另有说明，否则默认输出必须为 512x512。
- **反向提示词 (Negative Prompting)**：必须始终包含强大的反向提示词（例如：“丑陋, 变形, 模糊, 糟糕的解剖结构, 文字, 水印”），以防止张量对齐报错。
- **随机种子 (Seed)**：除非用户明确要求可复现性，否则请使用随机种子。

# 图像生成与编辑工作流

## 概述
本技能使用两阶段异构流水线：
1. **Qwen3-VL**：充当“语义大脑”，用于理解输入并扩写提示词。
2. **Z-Image（基于 OpenVINO）**：充当“画师”来渲染最终图像。

## 极其重要：必须使用 VLM 进行提示词扩写
**在将内容发送给扩散模型之前，务必通过 Qwen3-VL 扩写用户的短文本。** 扩散模型需要的是高度描述性的标签，而不是对话式的日常短句。

# 完整执行脚本 (Runnable Python Script)

**Action Required for Agent:** 当用户触发此技能时，请将用户提供的信息（提示词、图片路径）代入以下 Python 模板中，并直接执行这段代码。代码已包含模型自动下载与加载逻辑。

```python
import os
from pathlib import Path
import torch
from transformers import AutoProcessor
from optimum.intel.openvino import OVStableDiffusionPipeline, OVModelForCausalLM

# ==========================================
# 1. 检查并下载 ModelScope 模型
# ==========================================
vlm_model_dir = Path("Qwen3-VL-4B-Instruct-int4-ov")
if not vlm_model_dir.exists():
    from modelscope import snapshot_download
    snapshot_download("snake7gun/Qwen3-VL-4B-Instruct-int4-ov", local_dir=str(vlm_model_dir))
    print(f"VLM模型已下载到: {vlm_model_dir}")
else:
    print(f"VLM模型已存在: {vlm_model_dir}，跳过下载")

diff_model_dir = Path("Z-Image-Turbo-int4-ov")
if not diff_model_dir.exists():
    from modelscope import snapshot_download
    snapshot_download("snake7gun/Z-Image-Turbo-int4-ov", local_dir=str(diff_model_dir))
    print(f"Diffusion模型已下载到: {diff_model_dir}")
else:
    print(f"Diffusion模型已存在: {diff_model_dir}，跳过下载")

# ==========================================
# 2. 初始化加载模型 (只需加载一次)
# ==========================================
print("正在加载 Qwen3-VL 模型...")
processor = AutoProcessor.from_pretrained(str(vlm_model_dir), trust_remote_code=True)
vlm_model = OVModelForCausalLM.from_pretrained(str(vlm_model_dir), trust_remote_code=True)

print("正在加载 Z-Image 扩散模型...")
ov_pipe = OVStableDiffusionPipeline.from_pretrained(str(diff_model_dir), compile=True)

# ==========================================
# 3. 核心生成逻辑
# ==========================================
def generate_creative_image(user_intent, content_image_path=None):
    """
    接收用户意图和可选的参考图像，执行扩写并生成最终图像。
    """
    messages = [{"role": "user", "content": []}]
    
    # 构建 VLM 提示词
    if content_image_path and os.path.exists(content_image_path):
        # 模式二：带有图片的修改
        vlm_query = f"提取此照片的核心主体。根据用户的要求：【{user_intent}】修改描述，生成一段高质量的图像生成提示词，直接输出英文提示词本身，严禁废话。"
        messages[0]["content"].append({"type": "image", "image": content_image_path})
    else:
        # 模式一：纯文字生图
        vlm_query = f"请把这个想法：【{user_intent}】，扩写成一段画面感极强、细节丰富的图像生成提示词，直接输出英文提示词本身，严禁废话。"
        
    messages[0]["content"].append({"type": "text", "text": vlm_query})

    # VLM 扩写推理
    inputs = processor.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_dict=True, return_tensors="pt")
    generated_ids = vlm_model.generate(**inputs, max_new_tokens=300)
    generated_ids_trimmed = [out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)]
    expanded_prompt = processor.batch_decode(generated_ids_trimmed, skip_special_tokens=True)[0].strip()
    
    # 清理多余字符防报错
    clean_prompt = expanded_prompt.replace("\n", "").replace("*", "").strip()
    print(f"VLM 脑补的完整提示词: {clean_prompt}")

    # Diffusion 渲染
    print("正在驱动底层引擎渲染图像...")
    negative_prompt = "丑陋, 变形, 模糊, 糟糕的解剖结构, 极简, 缺维, 乱码, 水印, 文字, 签名, 低画质, 毁容"
    
    final_image = ov_pipe(
        prompt=clean_prompt,
        negative_prompt=negative_prompt,
        height=512,
        width=512,
        num_inference_steps=5, 
        guidance_scale=0.0
    ).images[0]
    
    output_path = "output_generated_image.png"
    final_image.save(output_path)
    print(f"图像生成成功！已保存至: {output_path}")
    return output_path

# ==========================================
# 4. Agent 执行入口
# ==========================================
# Agent: 请提取用户的真实意图并替换 user_intent 变量
user_intent = "一个小猫晒太阳的图片" 
result_path = generate_creative_image(user_intent=user_intent)
print(f"Final output generated at: {result_path}")