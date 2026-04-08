# 【Intel AI PC创新应用征文】+ 构建你的专属图像

## 环境配置

系统准备：

* 操作系统：Windows11
* Python：3.12
* GPU：RTX5060 Ti

requirements.txt提供了我所使用的Python库版本供参考，代码运行中极易出现库版本不对应导致的问题，例如：

```sh
Traceback (most recent call last):
  File "D:\Software\anaconda3\envs\openvino\Lib\site-packages\transformers\models\auto\configuration_auto.py", line 1271, in from_pretrained
    config_class = CONFIG_MAPPING[config_dict["model_type"]]
                   ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Software\anaconda3\envs\openvino\Lib\site-packages\transformers\models\auto\configuration_auto.py", line 966, in __getitem__
    raise KeyError(key)
KeyError: 'qwen3_vl'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "D:\wuzm\code\git_repo_wuzm\openvino_modelscope\qwen3_vl.py", line 12, in <module>
    model = OVModelForVisualCausalLM.from_pretrained(model_dir, device=device.value)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Software\anaconda3\envs\openvino\Lib\site-packages\optimum\intel\openvino\modeling_base.py", line 613, in from_pretrained
    return super().from_pretrained(
           ^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Software\anaconda3\envs\openvino\Lib\site-packages\optimum\modeling_base.py", line 368, in from_pretrained
    config = AutoConfig.from_pretrained(
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Software\anaconda3\envs\openvino\Lib\site-packages\transformers\models\auto\configuration_auto.py", line 1273, in from_pretrained
    raise ValueError(
ValueError: The checkpoint you are trying to load has model type `qwen3_vl` but Transformers does not recognize this architecture. This could be because of an issue with the checkpoint, or because your version of Transformers is out of date.

You can update Transformers with the command `pip install --upgrade transformers`. If this does not work, and the checkpoint is very new, then there may not be a release version that supports this model yet. In this case, you can get the most up-to-date code by installing Transformers from source with the command `pip install git+https://github.com/huggingface/transformers.git`
```

在运行Z-Image的图像生成代码中，没有装diffusers会出现：

```sh
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ImportError: cannot import name 'OVZImagePipeline' from 'optimum.intel.openvino' (D:\Software\anaconda3\envs\openvino\Lib\site-packages\optimum\intel\openvino\__init__.py)
```

```sh
pip install git+https://github.com/huggingface/diffusers.git@a1f36ee3ef4ae1bf98bd260e539197259aa981c1
```

## 应用场景说明

本项目旨在构建一个本地 AI 美术助理，将负责“看图和理解”的视觉大模型（Qwen3-VL）与负责画画的图像生成模型（Z-Image）结对串联。不需要繁琐的参数面板和提示词咒语，我们只需像日常聊天一样输入大白话，或者随手勾勒几笔火柴人，这个小助手就能通过Qwen3-VL理解图像信息，并实现复杂的模板生成工作，真正实现了零门槛的创意变现。支撑场景有：
1. 支持指定图像生成，可纯语言描述，也可手绘粗略图，指定风格，例如3D画风，表情包生成等；
2. 支持上传图像，文本描述修改内容，生成修改后的图像；
3. 支持上传原始图像和参考风格图像，也可自定义意见，生成新图像；

## 应用运行展示

场景一：基于语言描述生成图像，添加手绘图结合语言描述生成图像

![demo1](./assets/demo1.png)

![demo1](./assets/demo1-1.png)

场景二：基于语言描述提供对原始影像的编辑操作

![demo2](./assets/demo2.png)

场景三：提供参考影像风格，可添加文本描述，绘制对应的风格迁移后的图像

![demo3](./assets/demo3.png)

## Skills 运行展示

首先从https://modelscope.cn/studios/AgentScope/CoPaw/summary点击复制，设置未公开，会进入到如下界面：

![copaw](./assets/copaw.png)

首次使用对话，会需要配置模型：

![copaw-dashscope-settings](./assets/copaw-dashscope-settings.png)

配置好密钥之后红色框内选好使用的模型，再次回到chat界面即可对话，这里我选择的DashScope，输入自己的API Key：

![copaw-dashscope-settings1](./assets/copaw-dashscope-settings1.png)

在技能池界面点击右上角添加自己的skill

![skill-1](./assets/skill-1.png)

添加完成之后我们就能在对话中看到是否支持刚添加的skill：

![skill-2](./assets/skill-2.png)

## 总结与展望

这次OpenVINO的实践主要难点在于optimum-intel、openvino以及transformers等库的版本对应，具有较高的版本要求，否则极易出现问题。但不可否认，通过 INT4 量化，能在普通的个人 PC 上流畅运行庞大的多模态大模型和 Diffusion 渲染管道，这种彻底摆脱云端算力束缚的体验确实极具吸引力，也验证了 AI PC 的巨大潜力。

在魔搭创空间 Copaw 上将复杂的逻辑封装为 SKILL 是一次很有价值的探索。不过在实际开发中发现，如果过于依赖让 AI 自行试错和调整底层调用代码，大模型反复的报错重试会导致 Token 消耗极其巨大。

