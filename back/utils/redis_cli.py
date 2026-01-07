#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @author:anning
# @email:anningforchina@gmail.com
# @time:2024/10/26 10:12
# @file:redis.py
import hashlib

import django_redis
from functools import wraps

from utils.response import error_response

# Lazy Redis connection - only initialized when actually needed
rd = None


def get_redis_connection():
    global rd
    if rd is None:
        try:
            rd = django_redis.get_redis_connection("default")
        except NotImplementedError:
            # Fallback to a mock Redis object when Redis is not available
            rd = MockRedis()
    return rd


class MockRedis:
    """Mock Redis implementation for when Redis is not available"""
    def __init__(self):
        self.data = {}
        self.expires = {}

    def get(self, key):
        return self.data.get(key)

    def incr(self, key):
        if key not in self.data:
            self.data[key] = 0
        self.data[key] += 1
        return self.data[key]

    def expire(self, key, seconds):
        pass

    def hgetall(self, key):
        return self.data.get(key, {})

    def hexists(self, key, field):
        return key in self.data and field in self.data[key]

    def hdel(self, key, field):
        if key in self.data and field in self.data[key]:
            del self.data[key][field]
            return 1
        return 0

    def hlen(self, key):
        return len(self.data.get(key, {}))

    def delete(self, key):
        if key in self.data:
            del self.data[key]
            return 1
        return 0

    def pipeline(self):
        return self

    def hset(self, key, field, value):
        if key not in self.data:
            self.data[key] = {}
        self.data[key][field] = value
        return 1

    def execute(self):
        pass

    def rename(self, old_key, new_key):
        if old_key in self.data:
            self.data[new_key] = self.data[old_key]
            del self.data[old_key]

    def exists(self, key):
        return key in self.data

    def hmset(self, key, mapping):
        if key not in self.data:
            self.data[key] = {}
        self.data[key].update(mapping)
        return 1



def rate_limit(user_limit=100, ip_limit=200):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(view, request, *args, **kwargs):
            r = get_redis_connection()
            ip = request.META.get("REMOTE_ADDR")
            user = request.user if request.user.is_authenticated else None
            user_id = user.id if user else "anonymous"

            # 生成 Redis 键
            user_ip_key = f"user_ip:{user_id}_{ip}"
            ip_key = f"ip:{ip}"

            # 获取当前的请求计数
            user_ip_count = int(r.get(user_ip_key) or 0)
            ip_count = int(r.get(ip_key) or 0)

            # 检查限流条件
            if user_ip_count >= user_limit:
                return error_response(
                    429,
                    {"error": "已超过用户和IP的请求限制", "result": False},
                )
            if ip_count >= ip_limit:
                return error_response(
                    429, {"error": "已超过IP的请求限制", "result": False}
                )

            # 增加计数
            r.incr(user_ip_key)
            r.incr(ip_key)

            # 设置键的到期时间（每天重置）
            reset_time = 24 * 60 * 60  # 24小时
            r.expire(user_ip_key, reset_time)
            r.expire(ip_key, reset_time)

            # 调用原始视图函数
            return view_func(view, request, *args, **kwargs)

        return _wrapped_view

    return decorator


def generate_cache_key(page, platform, category):
    # 生成缓存 key，使用请求参数并进行 hash 防止过长
    key_string = f"page={page}&platform={platform}&category={category}"
    return hashlib.md5(key_string.encode()).hexdigest()
