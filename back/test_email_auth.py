#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
测试脚本：验证邮箱注册和登录功能
"""

import os
import django
import requests
import json

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ArticleManagePlus.settings')
django.setup()

def test_email_registration_and_login():
    """测试邮箱注册和登录功能"""
    base_url = "http://127.0.0.1:8000/api/user"
    
    print("开始测试邮箱注册和登录功能...")
    
    # 测试邮箱注册
    print("\n1. 测试邮箱注册...")
    register_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "nickname": "TestUser"
    }
    
    try:
        register_response = requests.post(f"{base_url}/register/", json=register_data)
        print(f"注册响应状态码: {register_response.status_code}")
        print(f"注册响应内容: {register_response.json()}")
        
        if register_response.status_code == 200:
            print("✓ 邮箱注册成功")
            # 提取token用于后续登录测试
            token_data = register_response.json().get('data', {})
            access_token = token_data.get('access')
        else:
            print("✗ 邮箱注册失败")
            return False
    except Exception as e:
        print(f"注册测试异常: {e}")
        return False
    
    # 测试邮箱登录
    print("\n2. 测试邮箱登录...")
    login_data = {
        "username": "test@example.com",  # 邮箱地址
        "password": "testpassword123"
    }
    
    try:
        login_response = requests.post(f"{base_url}/login/", json=login_data)
        print(f"登录响应状态码: {login_response.status_code}")
        print(f"登录响应内容: {login_response.json()}")
        
        if login_response.status_code == 200:
            print("✓ 邮箱登录成功")
        else:
            print("✗ 邮箱登录失败")
            return False
    except Exception as e:
        print(f"登录测试异常: {e}")
        return False
    
    # 测试通用认证接口
    print("\n3. 测试通用认证接口...")
    
    # 注册测试
    auth_register_data = {
        "action": "register",
        "email": "test2@example.com",
        "password": "testpassword123",
        "nickname": "TestUser2"
    }
    
    try:
        auth_register_response = requests.post(f"{base_url}/auth/", json=auth_register_data)
        print(f"通用注册响应状态码: {auth_register_response.status_code}")
        print(f"通用注册响应内容: {auth_register_response.json()}")
        
        if auth_register_response.status_code == 200:
            print("✓ 通用注册成功")
        else:
            print("✗ 通用注册失败")
    except Exception as e:
        print(f"通用注册测试异常: {e}")
    
    # 登录测试
    auth_login_data = {
        "action": "login",
        "username": "test2@example.com",
        "password": "testpassword123"
    }
    
    try:
        auth_login_response = requests.post(f"{base_url}/auth/", json=auth_login_data)
        print(f"通用登录响应状态码: {auth_login_response.status_code}")
        print(f"通用登录响应内容: {auth_login_response.json()}")
        
        if auth_login_response.status_code == 200:
            print("✓ 通用登录成功")
        else:
            print("✗ 通用登录失败")
    except Exception as e:
        print(f"通用登录测试异常: {e}")
    
    print("\n✓ 所有测试完成！")
    return True

if __name__ == "__main__":
    test_email_registration_and_login()