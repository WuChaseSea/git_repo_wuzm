# -*-coding:UTF-8 -*-
'''
* util.py
* @author wuzm
* created 2025/05/19 23:32:57
* @function: 
'''
import sqlite3
import pandas as pd
import yaml
import time
import random
import os
import pandas as pd

config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.yaml')
with open(config_path, 'r', encoding='utf-8') as file:
    config_data = yaml.safe_load(file)

# write a stream of words
def stream_data(line):
    for word in line.split():
        yield word + " "
        time.sleep(random.uniform(0.02, 0.05))

# Store the welcome message and introduction
def welcome_message():
    return config_data['welcome_template']

def introduction_message():
    return config_data['introduction_template']

def read_table():
    query = """
    SELECT * FROM new_fact_order_detail
    """
    conn = sqlite3.connect('data/order_database.db')
    df = pd.read_sql_query(query, conn)
    return df

def attribute_info(df):
    """
    Obtain the attributes, types, and head information of the DataFrame.
    """
    attributes = df.columns.tolist()
    dtypes_df = df.dtypes
    types_info = "\n".join([f"{index}:{dtype}" for index, dtype in dtypes_df.items()])
    head_info = df.head(10).to_csv()

    return attributes, types_info, head_info

if __name__ == "__main__":
    df = read_table()
