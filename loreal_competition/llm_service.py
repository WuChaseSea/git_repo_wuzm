# -*-coding:UTF-8 -*-
'''
* llm_service.py
* @author wzm
* created 2025/05/29 15:28:05
* @function: 
'''
import os
import yaml
import json
import re
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from langchain_community.chat_models.tongyi import ChatTongyi

config_path = os.path.join(os.path.dirname(__file__), 'config', 'template.yaml')
with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

def decide_questions(attributes, head_info, model_type = 2, user_api_key = None):
    """
    Determines the target attribute for modeling based on dataset attributes and characteristics.

    Parameters:
    - attributes: A list of dataset attributes.
    - head_info: A snapshot of the dataset's first few rows.
    - model_type (int, optional): The model type to use for decision making (default 4).
    - user_api_key (str, optional): The user's API key for OpenAI.

    Returns:
    - The name of the recommended target attribute. Please refer to prompt templates in config.py for details.

    Raises:
    - Exception: If unable to access the OpenAI API or another error occurs.
    """
    try:
        llm = ChatTongyi(model="qwen-plus", temperature=0)

        template = config["question_template"]
        
        prompt_template = PromptTemplate(input_variables=["attributes", "head_info"], template=template)
        summary_prompt = prompt_template.format(attributes=attributes, head_info=head_info)

        llm_answer = llm([HumanMessage(content=summary_prompt)])
        if '```json' in llm_answer.content:
            match = re.search(r'```json\n(.*?)```', llm_answer.content, re.DOTALL)
            if match: json_str = match.group(1)
        else: json_str = llm_answer.content
        json_result = json.loads(json_str)
        return [v for k, v in json_result.items()]
    except Exception as e:
        print(e)

def decide_name_correspondence(user_attribute, attributes, model_type = 2, user_api_key = None):
    """
    Determines the target attribute for modeling based on dataset attributes and characteristics.

    Parameters:
    - user_attribute: User attribute.
    - attributes: A list of dataset attributes.
    - model_type (int, optional): The model type to use for decision making (default 4).
    - user_api_key (str, optional): The user's API key for OpenAI.

    Returns:
    - The name of the recommended target attribute. Please refer to prompt templates in config.py for details.

    Raises:
    - Exception: If unable to access the OpenAI API or another error occurs.
    """
    try:
        llm = ChatTongyi(model="qwen-plus", temperature=0)
        
        template = config["decide_name_correspondence_template"]
        
        prompt_template = PromptTemplate(input_variables=["user_attribute", "attributes"], template=template)
        summary_prompt = prompt_template.format(user_attribute=user_attribute, attributes=attributes)

        llm_answer = llm([HumanMessage(content=summary_prompt)])
        if '```json' in llm_answer.content:
            match = re.search(r'```json\n(.*?)```', llm_answer.content, re.DOTALL)
            if match: json_str = match.group(1)
        else: json_str = llm_answer.content
        json_result = json.loads(json_str)
        import ipdb;ipdb.set_trace()
        return [v for k, v in json_result.items()]
    except Exception as e:
        print(e)
