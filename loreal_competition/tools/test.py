# -*-coding:UTF-8 -*-
'''
* test.py
* @author wuzm
* created 2025/05/19 11:02:24
* @function: test function
'''
import os, sys
sys.path.append('./')
from demo import daily_sales, sales_by_brand, orders_by_channel
from transformers import AutoTokenizer

if __name__ == "__main__":
    print(f"测试按日期统计销售额：")
    daily_sales_output = daily_sales()
    print(daily_sales_output)

    print(f"测试按品牌统计销售额：")
    brand_sales_output = sales_by_brand()
    print(brand_sales_output)

    print(f"测试按渠道统计订单数量：")
    orders_by_channel_output = orders_by_channel()
    print(orders_by_channel_output)


