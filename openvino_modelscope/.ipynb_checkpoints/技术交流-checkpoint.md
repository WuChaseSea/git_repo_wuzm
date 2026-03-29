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

## 应用运行展示

## Skills 运行展示

## 总结与展望
