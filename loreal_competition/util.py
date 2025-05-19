# -*-coding:UTF-8 -*-
'''
* util.py
* @author wuzm
* created 2025/05/19 23:32:57
* @function: 
'''
import sqlite3
import pandas as pd

def read_table():
    query = """
    SELECT * FROM new_fact_order_detail
    """
    conn = sqlite3.connect('data/order_database.db')
    df = pd.read_sql_query(query, conn)
    return df

if __name__ == "__main__":
    df = read_table()
