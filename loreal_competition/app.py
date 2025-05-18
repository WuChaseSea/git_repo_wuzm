import json
import re
import sqlite3
import pandas as pd
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
)
import gradio as gr


# ------------------------------------ 模型、数据初始化部分 ------------------------------------ #
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

tokenizer, model = get_qwen_model()

# ------------------------------------ 声明LLM能调用的函数 ------------------------------------ #
# 注意：
# 此部分的函数注释是一种固定格式，用于帮助LLM理解函数的功能
def daily_sales():
    """按日期统计最近十日日销售额，并打印到屏幕上

    Args:
        None

    Returns:
        包含每日销售额的字典，键为日期，值为销售额
    """
    query = """
    SELECT order_date, SUM(sales) AS total_sales
    FROM new_fact_order_detail
    GROUP BY order_date
    ORDER BY order_date
    LIMIT 10;
    """
    conn = sqlite3.connect('data/order_database.db')
    df = pd.read_sql_query(query, conn)
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

def qwen_func_response(message, history):
    if len(history)==0:
        return "你好！我是欧莱雅数据解构师，请问有什么可以帮您的？\n你可以问我“最近销售额情况”或者“告诉我渠道分销情况”"
    # 组合历史记录形成上下文
    messages = [
        {
            "role": "system",
            "content": "你是欧莱雅数据解构师，现在根据用户的要求提供相应的销售数据分析结果。当用户提出的问题没有对应的tools解决时，告知用户并介绍你能解决的问题。",
        }
    ]
    messages += history
    messages=[
        {
            "role":"user",
            "content":message
        }
    ]
    # 定义工具列表
    tools = [daily_sales, sales_by_brand, orders_by_channel]   
    # 运用聊天模版+转换为tokenizer
    text = tokenizer.apply_chat_template(messages, tools=tools, add_generation_prompt=True, tokenize=False)
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    # 模型生成 + 解码为字符串
    outputs = model.generate(**inputs, max_new_tokens=512)
    output_text = tokenizer.batch_decode(outputs)[0][len(text):]
    # 正则化处理
    messages.append(try_parse_tool_calls(output_text))
    # 针对函数调用进行处理
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
        # 将调用函数的结果加入进聊天内容，让模型再次推理
        text = tokenizer.apply_chat_template(messages, tools=tools, add_generation_prompt=True, tokenize=False)
        inputs = tokenizer(text, return_tensors="pt").to(model.device)
        outputs = model.generate(**inputs, max_new_tokens=512)
        output_text = tokenizer.batch_decode(outputs)[0][len(text):]
        messages.append(try_parse_tool_calls(output_text))
    # 输出结果
    return messages[-1]["content"]

# ------------------------------------ Streamlit 代码部分 ------------------------------------ #


# 创建 Gradio 对话界面
demo = gr.ChatInterface(
    qwen_func_response,
    type="messages",
    title="数据解构师 演示程序",
    description="目前仅做了一个简单的统计各地销售量的功能来演示，期待开发者有更多的idea",
    examples=["开启数据解构师"],
    run_examples_on_click=True,
    editable=True,
    save_history=True,
)

if __name__ == "__main__":
    demo.launch()