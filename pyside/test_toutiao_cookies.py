#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试头条号cookie-based UID检测功能
"""

import sys
import os
import time

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auto_browser.auto_base import AutoTools

def test_toutiao_cookies():
    """测试头条号cookie-based UID检测"""
    print("开始测试头条号cookie-based UID检测功能...")
    
    auto = AutoTools()
    
    try:
        print("正在打开头条号后台...")
        platform = "头条号"
        
        # 获取用户信息
        nickname, cookies, uid = auto.get_cookies(platform)
        
        print(f"\n测试结果:")
        print(f"- 昵称: {nickname if nickname else '未获取到'}")
        print(f"- UID: {uid if uid else '未获取到'}")
        print(f"- Cookie数量: {len(cookies) if cookies else 0}")
        
        if uid and nickname:
            print("\n✅ 测试成功! 成功获取到头条号UID")
        else:
            print("\n❌ 测试失败! 未能成功获取头条号UID")
            
    except Exception as e:
        print(f"\n测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_toutiao_cookies()
