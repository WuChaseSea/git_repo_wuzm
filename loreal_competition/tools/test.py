# -*-coding:UTF-8 -*-
'''
* test.py
* @author wuzm
* created 2025/05/19 11:02:24
* @function: test function
'''
import os, sys
sys.path.append('./')
from funciton_tools.trend_analysis import analyze_trend, plot_trend

if __name__ == "__main__":
    data = analyze_trend(
        "销售额", "订单日期", "D", "2024-03-01", "2024-03-30"
    )
    print(data)
    plot_trend(data, "销售额", "订单日期")


