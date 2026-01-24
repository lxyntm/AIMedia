#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/12/10 17:05
# @Author  : DNQTeach
# @File    : token_check.py
import json
import os
from datetime import datetime

from api.api_all import token_not_full, get_news_list


def check_user_token():
    """
    检查用户令牌
    Returns:
        tuple: (是否发布, 生成文章目录是否为空, API密钥, 选择的模型, 提示词)
    """
    file_path = 'opt.json'
    # 检查生成文章目录是否为空
    is_directory_empty = not token_not_full()
    
    if not is_directory_empty:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                content = json.load(file)
                selected_model = content['selected_model']
                api_key = content[selected_model]['api_key']
                prompt = content['prompt']
            if len(prompt)>0:
                return True,False,api_key,selected_model,prompt
            else:
                return True,False, api_key, selected_model, None
        else:
            return True,False,None,None,None
    else:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                content = json.load(file)
                selected_model = content['selected_model']
                api_key = content[selected_model]['api_key']
                prompt = content['prompt']
                if len(api_key) > 0:
                    if len(prompt)>0:
                        return True,True,api_key,selected_model,prompt
                    else:
                        return True,True,api_key,selected_model,None
                else:
                    return False,True,None,None,None
        else:
            return False,True,None,None,None