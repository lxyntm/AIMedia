#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
直接测试添加头条号账号的过程，用于调试JSON解析错误
"""

from auto_browser.auto_base import AutoTools
from api.api_all import create_account
from datetime import datetime, timedelta

def test_add_toutiao_account():
    """测试添加头条号账号"""
    print("开始测试添加头条号账号...")
    
    # 1. 获取头条号Cookie和UID
    auto = AutoTools()
    nickname, cookie, uid = auto.get_cookies("头条号")
    
    print(f"\n1. 获取到头条号信息:")
    print(f"   昵称: {nickname}")
    print(f"   UID: {uid}")
    print(f"   原始Cookie数量: {len(cookie)}")
    
    # 2. 简化Cookie数据
    simplified_cookies = [
        {"name": c.get('name', ''), "value": c.get('value', '')} 
        for c in cookie if c.get('name') and c.get('value')
    ]
    
    print(f"\n2. 简化后的Cookie:")
    print(f"   Cookie数量: {len(simplified_cookies)}")
    if simplified_cookies:
        print(f"   第一个Cookie: {simplified_cookies[0]}")
        print(f"   最后一个Cookie: {simplified_cookies[-1]}")
    
    # 3. 准备发送到后端的数据
    current_time = datetime.now()
    future_time = current_time + timedelta(days=30)
    formatted_future_time = future_time.strftime('%Y-%m-%d %H:%M:%S')
    
    data = {
        "nickname": nickname,
        "uid": uid,
        "platform": 0,  # 头条号对应平台代码0
        "expiry_time": formatted_future_time,
        "cookie": simplified_cookies,
        "status": 0
    }
    
    print(f"\n3. 准备发送到后端的数据:")
    print(f"   平台: {data['platform']}")
    print(f"   到期时间: {data['expiry_time']}")
    print(f"   状态: {data['status']}")
    
    # 4. 发送数据到后端
    print(f"\n4. 发送数据到后端...")
    try:
        result = create_account(data)
        print(f"   ✅ 添加成功! 结果: {result}")
    except Exception as e:
        print(f"   ❌ 添加失败! 错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_add_toutiao_account()