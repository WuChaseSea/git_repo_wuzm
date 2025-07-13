# ViewPaper结构设置

## 代码逻辑

启动目录 app.py
页面目录 apps/
模型目录 models/

INSGHTPAPER/
├── apps/                    # 核心界面目录
│   ├── assets/             # 前端界面文件
│   ├── db/             # 智能体实现模块
│   │   ├── __init__.py        # 基础智能体接口定义
│   │   ├── base_models.py       # 存储信息
│   │   ├── engine.py    # sqlite
│   │   ├── models.py       # 模型文件
│   ├── files/              # 文件管理
│   │   ├── ui.py        # 继承gradio的文件上传类
│   ├── index/              # 索引文件夹
│   │   ├── files        # 工具基础接口
│   │   ├── base.py  # BaseIndex的基础类
│   │   ├── manager.py  # IndexManager管理类
│   │   ├── models.py # SQLModel Index索引类
│   │   └── ui.py # IndexManagement展示类
│   ├── pages/            # 页面目录
│   │   ├── __init__.py       # 聊天页面设置
│   │   ├── chat_pannel.py    # 聊天页面组件
│   │   └── chat_suggestion.py    # 聊天页面组件
│   │   └── common.py    # 聊天页面组件
│   │   └── control.py    # 聊天页面组件
│   │   └── demo_hint.py    # 聊天页面组件
│   │   └── paper_list.py    # 聊天页面组件
│   │   └── report.py    # 聊天页面组件
│   │   └── settings.py    # 用户设置文件
│   │   └── setup.py    # 配置页面
│   ├── reasoning/            # 推理模块
│   │   ├── prompt_optimization       # prompt设置
│   │   ├── base.py    # 基础推理类
│   │   └── simple.py    # 普通推理类
│   ├── utils/            # 函数目录
│   │   ├── commands.py       # 命令
│   │   ├── hf_papers.py    # paperlist
│   │   └── lang.py    # 语言设置
│   │   ├── rate_limit.py    # 速率设置
│   │   └── render.py    # 文本渲染
│   └── base.py          # BaseAPP
│   └── components.py          # 基础组件
│   └── exceptions.py          # exception管理
│   └── extension_protocol.py          # 扩展工具
│   └── main.py          # APP
│   └── settings.py          # 设置类
├── models/                # 核心模型目录
│   ├── base # 基础类
│   └── indices        # 支持的文件索引
│   └── loaders        # embedding索引
│   └── storages        # 索引存储
├── app.py               # 主程序入口
├── flowsettings.py           # 以前的设置文件
├── settings.py              # 现在的设置文件

## 设置说明

VP_DEMO_MODE 是否是演示模型，一般是False
