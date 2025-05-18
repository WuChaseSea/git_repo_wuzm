import json
import re
import sqlite3
import pandas as pd
import streamlit as st
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
)


# ------------------------------------ 模型、数据初始化部分 ------------------------------------ #
@st.cache_resource
def get_qwen_model():
    model_name_or_path = "./Qwen2.5-7B-Instruct"
    # 加载 Qwen2.5-7B-Instruct 模型和分词器
    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
    model = AutoModelForCausalLM.from_pretrained(
        model_name_or_path,
        torch_dtype="auto",
        device_map="auto",
    )
    return tokenizer, model

# ------------------------------------ 声明LLM能调用的函数 ------------------------------------ #
# 注意：
# 此部分的函数注释是一种固定格式，用于帮助LLM理解函数的功能
def daily_sales():
    """按日期统计每日销售额，并打印到屏幕上

    Args:
        None

    Returns:
        包含每日销售额的字典，键为日期，值为销售额
    """
    query = """
    SELECT order_date, SUM(sales) AS total_sales
    FROM new_fact_order_detail
    GROUP BY order_date
    ORDER BY order_date;
    """
    conn = sqlite3.connect('data/order_database.db')
    df = pd.read_sql_query(query, conn)
    st.dataframe(df)
    return df.set_index('order_date')['total_sales'].to_dict()

def sales_by_brand():
    """按品牌统计销售额，并打印到屏幕上

    Args:
        None

    Returns:
        包含各品牌销售额的字典，键为品牌代码，值为销售额
    """
    conn = sqlite3.connect('data/order_database.db')
    query = """
    SELECT brand_code, SUM(sales) AS total_sales
    FROM new_fact_order_detail
    GROUP BY brand_code
    ORDER BY total_sales DESC;
    """
    conn = sqlite3.connect('data/order_database.db')
    df = pd.read_sql_query(query, conn)
    st.dataframe(df)
    return df.set_index('brand_code')['total_sales'].to_dict()

def orders_by_channel():
    """按渠道统计订单数量，并打印到屏幕上

    Args:
        None

    Returns:
        包含各渠道订单数量的字典，键为渠道名称，值为订单数量
    """
    query = """
    SELECT channel, COUNT(order_no) AS order_count
    FROM new_fact_order_detail
    GROUP BY channel
    ORDER BY order_count DESC;
    """
    conn = sqlite3.connect('data/order_database.db')
    df = pd.read_sql_query(query, conn)
    st.dataframe(df)
    return df.set_index('channel')['order_count'].to_dict()

# ------------------------------------ LLM调用函数和回复逻辑 ------------------------------------ #
def try_parse_tool_calls(content: str):
    """此函数用于处理LLM函数调用"""
    tool_calls = []
    offset = 0
    for i, m in enumerate(re.finditer(r"<tool_call>\n(.+)?\n</tool_call>", content)):
        if i == 0:
            offset = m.start()
        try:
            func = json.loads(m.group(1))
            tool_calls.append({"type": "function", "function": func})
            if isinstance(func["arguments"], str):
                func["arguments"] = json.loads(func["arguments"])
        except json.JSONDecodeError as e:
            print(f"Failed to parse tool calls: the content is {m.group(1)} and {e}")
            pass
    if tool_calls:
        if offset > 0 and content[:offset].strip():
            c = content[:offset]
        else: 
            c = ""
        return {"role": "assistant", "content": c, "tool_calls": tool_calls}
    return {"role": "assistant", "content": re.sub(r"<\|im_end\|>$", "", content)}

def qwen_func_response():
    tokenizer, model = get_qwen_model()
    tools = [daily_sales, sales_by_brand, orders_by_channel]   # 定义工具列表
    messages = [*st.session_state.messages]    # 获取历史聊天
    text = tokenizer.apply_chat_template(messages, tools=tools, add_generation_prompt=True, tokenize=False)
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=512)
    output_text = tokenizer.batch_decode(outputs)[0][len(text):]
    messages.append(try_parse_tool_calls(output_text))
    if tool_calls := messages[-1].get("tool_calls", None):
        for tool_call in tool_calls:
            if fn_call := tool_call.get("function"):
                fn_name: str = fn_call["name"]
                fn_args: dict = fn_call["arguments"]
                function = next((func for func in tools if func.__name__ == fn_name), None) # 检索工具
                if function is not None:
                    fn_res: str = json.dumps(function(**fn_args))
                    messages.append({
                        "role": "tool",
                        "name": fn_name,
                        "content": fn_res,
                    })
        text = tokenizer.apply_chat_template(messages, tools=tools, add_generation_prompt=True, tokenize=False)
        inputs = tokenizer(text, return_tensors="pt").to(model.device)
        outputs = model.generate(**inputs, max_new_tokens=512)
        output_text = tokenizer.batch_decode(outputs)[0][len(text):]
        messages.append(try_parse_tool_calls(output_text))
    return messages[-1]["content"]

# ------------------------------------ Streamlit 代码部分 ------------------------------------ #
st.title("数据解构师 演示程序")
st.text("目前仅做了一个简单的统计各地销售量的功能来演示，期待开发者有更多的idea")
# 初始提示词
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "你是欧莱雅数据解构师，现在根据用户的要求提供相应的销售数据分析结果。当用户提出的问题没有对应的tools解决时告知用户并介绍你能解决的问题。"}]

# 显示聊天历史记录
for message in st.session_state.messages:
    if message["role"]=='system':   # 不打印提示词
        continue
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 接受用户输入
if prompt := st.chat_input("按日期统计每日销售额"):
    # 将用户输入添加进聊天历史记录
    st.session_state.messages.append({"role": "user", "content": prompt})
    # 将用户输入打印到屏幕上
    with st.chat_message("user"):
        st.markdown(prompt)
    # 打印模型输出到屏幕上
    with st.chat_message("assistant"):
        response = st.markdown(qwen_func_response())  # 获取模型输出
    # 将模型输出打印到屏幕上
    st.session_state.messages.append({"role": "assistant", "content": response})