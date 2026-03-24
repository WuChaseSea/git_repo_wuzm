from pathlib import Path
from notebook_utils import device_widget

device = device_widget(default="AUTO", exclude=["NPU"])

model_dir = Path(f"D:\wuzm\models\Qwen3-VL-4B-Instruct-ov-int4")

print(device)

from optimum.intel.openvino import OVModelForVisualCausalLM

model = OVModelForVisualCausalLM.from_pretrained(model_dir, device=device.value)
print("✅ 模型加载完成")
