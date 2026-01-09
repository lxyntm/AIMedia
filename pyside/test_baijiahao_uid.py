#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专门测试百家号UID获取功能的脚本
"""

import sys
import os

# 添加项目路径到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from auto_browser.auto_base import AutoTools

def test_baijiahao_uid():
    """测试百家号UID获取功能"""
    print("开始测试百家号UID获取功能...")
    try:
        auto = AutoTools()
        nickName, cookies, uid = auto.get_cookies('百家号')
        print(f"\n=== 测试结果 ===")
        print(f"昵称: {nickName}")
        print(f"UID: {uid}")
        print(f"Cookies数量: {len(cookies)}")
        
        if uid:
            print("✓ 成功获取到UID")
        else:
            print("✗ 未能获取到UID")
            print("\n请检查以下几点:")
            print("1. 是否成功登录百家号")
            print("2. 浏览器中是否可以看到ab_bid或ab_jid cookies")
            print("3. 网络连接是否正常")
            
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_baijiahao_uid()
