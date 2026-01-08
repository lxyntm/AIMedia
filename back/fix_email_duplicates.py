#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
脚本功能：修复用户表中重复的email值，确保唯一性约束能够正确应用
"""

import os
import sys
import django
from django.contrib.auth import get_user_model

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ArticleManagePlus.settings')
django.setup()

User = get_user_model()

def fix_email_duplicates():
    """修复重复的email值"""
    print("开始检查重复的email...")
    
    # 检查当前用户数据
    users = User.objects.all()
    email_count = {}
    duplicate_emails = []
    
    for user in users:
        email = user.email
        if email:
            if email in email_count:
                email_count[email] += 1
            else:
                email_count[email] = 1
    
    # 找出重复的email
    duplicate_emails = [email for email, count in email_count.items() if count > 1]
    
    if duplicate_emails:
        print(f"发现重复的email: {duplicate_emails}")
        for email in duplicate_emails:
            print(f"  {email}: {email_count[email]} 个用户")
            
        # 为重复的email生成唯一值
        for email in duplicate_emails:
            users_with_email = User.objects.filter(email=email)
            for i, user in enumerate(users_with_email):
                if i == 0:
                    # 保留第一个用户的email
                    continue
                else:
                    # 为其他用户生成唯一email
                    new_email = f"{email.split('@')[0]}+{i}@{email.split('@')[1]}"
                    user.email = new_email
                    user.save()
                    print(f"更新用户 {user.id} 的email为: {new_email}")
    else:
        print("没有发现重复的email")
    
    # 检查是否有空的email（如果email是唯一的，应该允许空值，但不能有重复的空值）
    empty_email_users = User.objects.filter(email__isnull=True)
    print(f"空email的用户数量: {empty_email_users.count()}")
    
    # 检查email为''的用户
    empty_string_email_users = User.objects.filter(email='')
    print(f"email为空字符串的用户数量: {empty_string_email_users.count()}")
    
    if empty_string_email_users.count() > 1:
        print("发现多个email为空字符串的用户，需要处理")
        for i, user in enumerate(empty_string_email_users):
            if i == 0:
                continue
            else:
                user.email = f"user{i}@example.com"
                user.save()
                print(f"更新用户 {user.id} 的email为: {user.email}")
    
    print("修复完成")

if __name__ == "__main__":
    fix_email_duplicates()