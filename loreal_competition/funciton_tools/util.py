from funciton_tools.trend_analysis import analyze_trend, plot_trend, analyze_distribution, plot_distribution

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "analyze_trend",
            "description": "分析某个指标在一段时间内的趋势，支持按天/周/月聚合。",
            "parameters": {
                "type": "object",
                "properties": {
                    "value_column": {
                        "type": "string",
                        "description": "要分析的数值字段，如销售额"
                    },
                    "time_column": {
                        "type": "string",
                        "description": "表示时间的列名，如日期"
                    },
                    "freq": {
                        "type": "string",
                        "enum": ["D", "W", "M"],
                        "description": "聚合频率，D=日，W=周，M=月"
                    },
                    "start": {
                        "type": "string",
                        "description": "起始时间（格式：YYYY-MM-DD）",
                        "nullable": True
                    },
                    "end": {
                        "type": "string",
                        "description": "结束时间（格式：YYYY-MM-DD）",
                        "nullable": True
                    }
                },
                "required": ["value_column", "time_column"]
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "plot_trend",
            "description": "绘制时间序列趋势图。",
            "parameters": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "object",
                        "description": "要绘制的数据"
                    },
                    "value_column": {
                        "type": "string",
                        "description": "要分析的数值字段，如销售额"
                    },
                    "time_column": {
                        "type": "string",
                        "description": "表示时间的列名，如日期"
                    }
                },
                "required": ["data", "value_column", "time_column"]
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_distribution",
            "description": "按某字段对数值字段进行聚合统计",
            "parameters": {
                "type": "object",
                "properties": {
                    "group_by_field": {
                        "type": "string",
                        "description": "要绘制的数据"
                    },
                    "agg_field": {
                        "type": "string",
                        "description": "要分析的数值字段，如销售额"
                    },
                    "agg_func": {
                        "type": "string",
                        "description": "表示时间的列名，如日期",
                        "enum": ["count", "sum", "avg"]
                    }
                },
                "required": ["group_by_field", "agg_field"]
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "plot_distribution",
            "description": "绘制分布图",
            "parameters": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "object",
                        "description": "要绘制的数据"
                    },
                    "chart_type": {
                        "type": "string",
                        "description": "要分析的数值字段，如销售额",
                        "enum": ["bar", "pie"]
                    },
                    "title": {
                        "type": "string",
                        "description": "表示时间的列名，如日期"
                    }
                },
                "required": ["data", "chart_type"]
            },
        },
    }
]

functions = [tool["function"] for tool in TOOLS]

def get_function_by_name(name):
    if name == "analyze_trend":
        return analyze_trend
    if name == "plot_trend":
        return plot_trend
    if name == "analyze_distribution":
        return analyze_distribution
    if name == "plot_distribution":
        return plot_distribution
