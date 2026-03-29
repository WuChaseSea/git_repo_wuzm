from pathlib import Path
from notebook_utils import device_widget

device = device_widget(default="AUTO", exclude=["NPU"])

model_dir = Path(r"D:\wuzm\models\Qwen3-VL-4B-Instruct-ov-int4")

print(device)

from optimum.intel.openvino import OVModelForVisualCausalLM

model = OVModelForVisualCausalLM.from_pretrained(model_dir, device=device.value)
print("✅ 模型加载完成")

from PIL import Image
from transformers import AutoProcessor, TextStreamer
from pathlib import Path
import requests

min_pixels = 256 * 28 * 28
max_pixels = 1280 * 28 * 28
processor = AutoProcessor.from_pretrained(model_dir, min_pixels=min_pixels, max_pixels=max_pixels)

# 下载示例图片
example_image_path = Path("demo.jpeg")


image = Image.open(example_image_path)
question = "请描述这张图片的内容。"

messages = [
    {
        "role": "user",
        "content": [
            {"type": "image", "image": "demo.jpeg"},
            {"type": "text", "text": question},
        ],
    }
]

inputs = processor.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_dict=True, return_tensors="pt")


generated_ids = model.generate(**inputs, max_new_tokens=200, streamer=TextStreamer(processor.tokenizer, skip_prompt=True, skip_special_tokens=True))
print(generated_ids)
