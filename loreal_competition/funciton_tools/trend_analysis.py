# -*-coding:UTF-8 -*-
'''
* trend_analysis.py
* @author wuzm
* created 2025/05/20 10:55:24
* @function: 趋势分析相关代码
'''
import os
import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st

from funciton_tools.table_info import FIELD_MAPPING

def read_table():
    query = """
    SELECT * FROM new_fact_order_detail
    """
    conn = sqlite3.connect('./data/order_database.db')
    df = pd.read_sql_query(query, conn)
    return df

def analyze_trend(
        value_column: str,
        time_column: str,
        freq: str = 'M',
        start: str = None,
        end: str = None
        ):
    """统计某个字段的时间序列趋势变化情况。

    Args:
        value_column: 要分析的数值列，如 '销售额'
        time_column: 时间列，如 '日期'
        freq: 聚合频率，'D'、'W'、'M'
        start: 起始时间（可选）
        end: 结束时间（可选）

    Returns:
        查询结果
    """
    data = read_table()
    # 时间格式转换
    if value_column not in list(data):
        value_column = FIELD_MAPPING[value_column]
    time_column = FIELD_MAPPING["订单日期"]
    data[time_column] = pd.to_datetime(data[time_column])

    # 时间筛选
    if start:
        data = data[data[time_column] >= pd.to_datetime(start)]
    if end:
        data = data[data[time_column] <= pd.to_datetime(end)]
    
    # 按频率聚合
    grouped = data.groupby(pd.Grouper(key=time_column, freq=freq))[value_column].sum().reset_index()
    grouped[time_column] = grouped[time_column].dt.strftime('%Y-%m-%d')
    grouped = grouped.set_index(time_column)[value_column].to_dict()
    st.session_state.df_cache = []
    st.session_state.df_cache.append(grouped)
    # 绘图
    # fig = px.line(grouped, x=time_column, y=value_column, title=f"{value_column} 趋势分析", markers=True)
    return {
        "type": "table",
        "content": grouped
    }

def plot_trend(
        data: pd.DataFrame,
        value_column: str,
        time_column: str,
):
    """绘制时间序列趋势图。

    Args:
        data: 需要绘制的数据
        value_column: 要分析的数值列，如 '销售额'
        time_column: 时间列，如 '日期'

    Returns:
        
    """
    if value_column not in list(data):
        value_column = FIELD_MAPPING[value_column]
    time_column = FIELD_MAPPING["订单日期"]
    data = pd.DataFrame({time_column: data.keys(), value_column: data.values()})
    fig = px.line(data, x=time_column, y=value_column, title=f"{value_column} 趋势分析", markers=True)
    return {
        "type": "plot",
        "content": fig
    }
    # st.plotly_chart(fig)

def analyze_distribution(group_by_field: str, agg_field: str, agg_func: str = "count"):
    """按某字段对数值字段进行聚合统计。

    Args:
        group_by_field: 需要绘制的数据
        agg_field: 要分析的数值字段
        agg_func: 对数值字段进行的操作，包括

    Returns:
        
    """
    sql = f"""
        SELECT {group_by_field} AS category, 
               {agg_func}({agg_field}) AS value
        FROM new_fact_order_detail
        GROUP BY {group_by_field}
        ORDER BY value DESC
    """
    conn = sqlite3.connect('./data/order_database.db')
    df = pd.read_sql_query(sql, conn)
    # 缓存用于图表绘制
    st.session_state.df_cache = []
    st.session_state.df_cache.append(df)
    return {
        "type": "table",
        "content": df.to_dict(orient="records")
    }

def plot_distribution(data: list, chart_type: str = "bar", title: str = "分布图"):
    """绘制分布图。

    Args:
        data: 需要绘制的数据
        chart_type: 绘制的图表类型，包括柱状图、饼图
        title: 图表标题

    Returns:
        
    """
    df = pd.DataFrame(data)
    if chart_type == "bar":
        fig = px.bar(df, x="category", y="value", title=title)
    elif chart_type == "pie":
        fig = px.pie(df, names="category", values="value", title=title)
    else:
        raise ValueError("Unsupported chart type")
    return {
        "type": "plot",
        "content": fig
    }
