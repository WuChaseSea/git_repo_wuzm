# -*-coding:UTF-8 -*-
'''
* streamlit_run.py
* @author wuzm
* created 2025/05/20 14:40:41
* @function: streamlit 运行程序
'''
import time
import streamlit as st

from util import welcome_message, introduction_message, stream_data

from model import llm_chat

def render_function_output(output):
    if isinstance(output, dict):
        if output["type"] == "text":
            st.markdown(output["content"])
        elif output["type"] == "plot":
            st.plotly_chart(output["content"], use_container_width=True)
        elif output["type"] == "table":
            st.dataframe(output["content"])
    else:
        st.markdown(str(output))

st.set_page_config(page_title="BeautyInsight Agent", page_icon=":rocket:", layout="wide")
if "system_messages" not in st.session_state:
    st.session_state.system_messages = [
        {"role": "system", "content": "你是一个数据分析师，现在根据用户的要求提供相应的销售数据分析结果。当用户提出的问题没有对应的tools解决时告知用户并介绍你能解决的问题。"},
        # {"role": "user",  "content": "帮我分析2024年上半年每日销售额的变化情况"},
    ]
# TITLE SECTION
with st.container():
    st.title("Welcome to BeautyInsight Agent!")
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
    if st.session_state.initialized:
        st.session_state.welcome_message = welcome_message()
        st.write(stream_data(st.session_state.welcome_message))
        # st.session_state.introduction_message = introduction_message()
        # st.write(stream_data(st.session_state.introduction_message))
        time.sleep(0.5)
        st.write("[Github > ](https://github.com/WuChaseSea/git_repo_wuzm.git)")
        st.session_state.initialized = False
    else:
        st.write(st.session_state.welcome_message)
        st.write("[Github > ](https://github.com/WuChaseSea/git_repo_wuzm.git)")

st.session_state.outputs = []
# 显示聊天历史记录
# for message in st.session_state.system_messages:
#     if message["role"]=='system':   # 不打印提示词
#         continue
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# 接受用户输入
if prompt := st.chat_input("分析2024年上半年每日销售额的变化情况并绘制图表分析"):
    # 将用户输入添加进聊天历史记录
    # 将用户输入打印到屏幕上
    st.session_state.outputs.append([])
    with st.chat_message("user"):
        st.markdown(prompt)
    # 打印模型输出到屏幕上
    response = llm_chat({"role": "user", "content": prompt})  # 获取模型输出
    with st.chat_message("assistant"):
        for output in st.session_state.outputs[-1]:
            render_function_output(output)
        st.markdown(response)
    # 将模型输出打印到屏幕上