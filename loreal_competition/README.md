# 赛题3：数据解构师 演示程序

## 赛题描述

数据蕴藏着解锁未来美妆趋势的钥匙，在企业内部有大量数据分析的需求，对于非技术人员来说，在实现快速数据可视化以及数据洞察方面仍然存在技术障碍（例如需要掌握工具，使用代码等）。
我们希望参赛者开发一款基于大语言模型的对话式数据分析工具，让即使不熟悉代码和复杂数据操作的业务人员也能轻松地通过自然语言与数据进行交互，快速获取数据洞察，并辅助业务决策。

## 演示案例程序使用方法

### 搭建环境&下载所需数据

**前置要求**

首先需要确保电脑正确的安装了python，并且版本大于3.11。

推荐电脑配置包含一块显存大于16G的Nvidia显卡，并且正确的安装了驱动。

**环境安装**

使用如下命令自动完成环境安装

```bash
pip install -r requirements.txt
```

**模型下载(可选)**

推荐使用modelscope完成模型下载，本次演示使用[Qwen2.5的7B Instruct版本模型](https://modelscope.cn/models/Qwen/Qwen2.5-7B-Instruct/summary)。

运行代码时会自动下载所需模型，当然也可以直接运行模型下载命令，命令如下：

```bash
modelscope download --model Qwen/Qwen2.5-7B-Instruct --local_dir ./Qwen2.5-7B-Instruct
```

**下载数据集 + 构建数据库**

请在赛题官网完成数据集下载，并将其解压到`./data`目录下。

使用如下命令构建数据库

```bash
python import_csv_to_sqlite.py
```

### 运行使用

使用如下命令执行gradio 案例程序

```bash
python app.py
```

使用如下命令执行streamlit案例程序

```bash
streamlit run streamlit_run.py
```

streamlit支持更丰富的表格形式，如折线图、直方图等，推荐大家使用！；）