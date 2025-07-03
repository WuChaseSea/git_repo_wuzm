# BASEMANUS

本项目基于OPENMANUS学习；

OpenManus/
├── app/                    # 核心应用目录
│   ├── agent/             # 智能体实现模块
│   │   ├── base.py        # 基础智能体接口定义
│   │   ├── manus.py       # 主要智能体实现
│   │   ├── planning.py    # 任务规划模块
│   │   ├── react.py       # 反应式决策模块
│   │   ├── swe.py         # 软件工程相关能力
│   │   └── toolcall.py    # 工具调用处理模块
│   ├── flow/              # 流程控制模块
│   │   ├── base.py        # 流程管理基础类
│   │   ├── flow_factory.py # 流程工厂
│   │   └── planning.py     # 任务规划流程
│   ├── tool/              # 工具集合模块
│   │   ├── base.py        # 工具基础接口
│   │   ├── browser_use_tool.py  # 浏览器操作工具
│   │   ├── file_saver.py  # 文件操作工具
│   │   ├── google_search.py # 搜索工具
│   │   └── python_execute.py # Python代码执行工具
│   ├── prompt/            # 系统提示词模块
│   │   ├── manus.py       # Manus智能体提示词
│   │   ├── planning.py    # 规划相关提示词
│   │   └── toolcall.py    # 工具调用提示词
│   └── config.py          # 配置管理
├── config/                # 配置文件目录
│   ├── config.example.toml # 配置文件示例
│   └── config.toml        # 实际配置文件
├── main.py               # 主程序入口
├── run_flow.py           # 流程运行脚本
├── setup.py              # 项目安装配置
└── requirements.txt      # 项目依赖列表

## 环境准备

```sh
conda create -n manus python=3.12
pip install -r requirements.txt

playwright install chromium
```

## 逻辑分析

agent 智能体实现目录

* base.py 定义了 BaseAgent 抽象类，run函数调用step函数；
* react.py 定义了 ReActAgent 类，添加了 think、act函数，重写了step函数；
* toolcall.py 定义了 ToolCallAgent 类，继承ReActAgent，重写了 think、act函数，run函数调用父类的run；
* manus.py 定义了 Manus 类，继承 ToolCallAgent，根据具体需求重写 think函数；

base run函数里面调用20次step，每一次step函数都包含一个think和act操作；
