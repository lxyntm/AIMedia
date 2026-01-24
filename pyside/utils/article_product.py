#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/12/10 14:19
# @Author  : DNQTeach
# @File    : articl_product.py
from ai_model.writing_assistant import WritingAssistant
from api.api_all import token_not_full, get_news_list
from utils.get_server_key import run_decrypt
import json

def get_is_sys_api_key():
    """
    获取是否使用系统内部模型
    Returns:
        bool: True 表示使用系统内部模型，False 表示使用用户自定义模型
    """
    try:
        print("===== get_is_sys_api_key() called =====")
        # 优先从后端 API 获取系统模型配置
        from api.api_all import get_system_model_config
        print("1. Attempting to get system model config from API")
        config = get_system_model_config()
        print(f"2. API response: {config}")
        
        if config:
            if isinstance(config, dict) and 'use_system_model' in config:
                print(f"3. Using system model config from API: {config['use_system_model']}")
                return config['use_system_model']
            else:
                print(f"3. Invalid config format from API: {config}")
        else:
            print("3. No config returned from API")
        
        # 如果 API 获取失败，从本地配置文件读取
        print("4. Attempting to read local config file")
        try:
            with open('opt.json', 'r', encoding='utf-8') as f:
                local_config = json.load(f)
            print(f"5. Local config: {local_config}")
            # 检查是否存在 use_system_model 配置
            if 'use_system_model' in local_config:
                print(f"6. Using system model config from local: {local_config['use_system_model']}")
                return local_config['use_system_model']
            else:
                print("6. No use_system_model in local config")
        except Exception as e:
            print(f"5. Error reading local config: {e}")
        
        # 默认使用系统内部模型
        print("7. Using default system model config: False")
        return False
    except Exception as e:
        print(f"Error in get_is_sys_api_key: {e}")
        import traceback
        traceback.print_exc()
        # 出错时默认使用系统内部模型
        print("Using default system model config due to error: False")
        return False


def article_create(topic, selected_model, api_key, prompt, is_directory_empty):
    """
    创建文章内容
    Args:
        topic: 文章主题
        selected_model: 选择的模型
        api_key: API密钥
        prompt: 提示词
        is_directory_empty: 生成文章目录是否为空
    Returns:
        tuple: (文章内容, token使用量, 是否启用)
    """
    try:
        model_config = [selected_model, api_key, prompt]
        print(f"用户配置模型: {selected_model}, 文章目录是否为空: {not is_directory_empty}")
        # 创建 WritingAssistant 实例
        try:
            # 获取生成文章是否不为空
            if not is_directory_empty: #生成文章目录不为空，此处需要修改，不是从热点里读取文章，是从已生成的文章中读取文章
                # 待发布文章目录不为空的话，读取现有的文章
                is_sys_api_key = get_is_sys_api_key() # 是否使用内部模型
                if is_sys_api_key:
                    print("用系统模型APIkey")
                    # 获取系统模型API密钥
                    apikey = run_decrypt()
                    print(f"系统模型API密钥: {apikey}")
                    if prompt is not None:
                        assistant = WritingAssistant(prompt=prompt, api_key=apikey)
                    else:
                        print("走这里")
                        assistant = WritingAssistant(api_key=apikey)
                else:
                    print("使用用户的 APIkey")
                    if None not in model_config:
                        assistant = WritingAssistant(mod=selected_model, api_key=api_key, prompt=prompt)
                    else:
                        assistant = WritingAssistant(mod=selected_model, api_key=api_key)
            else: #生成文章目录为空
                news_list = get_news_list(params={'topic': topic})
                if news_list and len(news_list['results']) > 0:
                    article = news_list['results'][0]['new_content']
                    usetokens = news_list['results'][0]['use_token']
                    return article, usetokens, is_directory_empty
                
        except Exception as e:
            print(f"Error creating WritingAssistant: {str(e)}")
            return False, None, False

        # 生成文章
        if not assistant or not hasattr(assistant, 'generate_article'):
            print("Invalid WritingAssistant instance")
            return False, None, False

        result = assistant.generate_article(topic)
        
        if not result or not isinstance(result, dict) or 'content' not in result or not result['content']:
            print(f"No valid content in generation result: {result}")
            return False, None, False

        article = result["content"].replace("**", "").replace('### ', '').replace('标题：', '')
        usetokens = result.get('token_usage', {}).get('total_tokens', 0)
        
        if not article or len(article.strip()) == 0:
            print("Empty article generated")
            return False, None, False

        return article, usetokens, is_directory_empty

    except Exception as e:
        print(f"Error in article_create: {str(e)}")
        return False, None, False
