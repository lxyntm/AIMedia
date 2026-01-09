#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 测试nickname处理逻辑
account_data = {
    'platform': '百家号',
    'nickname': '',
    'uid': '1853833051607377',
    'cookie': []
}

# 原始逻辑
original_nickname = account_data["nickname"]
print(f'原始nickname: "{original_nickname}"')

# 修复后逻辑
fixed_nickname = account_data["nickname"] or f"{account_data['platform']}_用户_{account_data['uid'][:8]}"
print(f'修复后nickname: "{fixed_nickname}"')

# 测试有昵称的情况
account_data_with_nickname = {
    'platform': '百家号',
    'nickname': '测试用户',
    'uid': '1853833051607377',
    'cookie': []
}

fixed_nickname_with_name = account_data_with_nickname["nickname"] or f"{account_data_with_nickname['platform']}_用户_{account_data_with_nickname['uid'][:8]}"
print(f'有昵称时的修复后nickname: "{fixed_nickname_with_name}"')
