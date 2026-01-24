#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/12/29 15:39
# @Author  : DNQTeach
# @File    : get_server_key.py


import base64
import hashlib


from cryptography.fernet import Fernet

from api.api_all import get_user, get_gml_key, token_not_full
from PySide6.QtCore import QSettings

def generate_key_from_string(input_string):
    key = "F4FQgz11cd-C4JFWXsd8mViLp6nLIUi6XDZ9Ca5hkls="
    # 将时间戳和输入字符串拼接
    combined = f"{input_string}:{key}"
    # 使用 SHA-256 哈希生成固定长度的密钥
    hash_value = hashlib.sha256(combined.encode('utf-8')).digest()
    # 将哈希值转换为 Base64 编码的 Fernet 密钥
    key = base64.urlsafe_b64encode(hash_value[:32])  # 取前 32 字节
    return key

# 初始化加密器
def initialize_fernet(key):
    return Fernet(key)


# 解密字符串
def decrypt_string(fernet, encrypted_text):
    try:
        # 将字符串编码为字节
        encrypted_bytes = encrypted_text.encode('utf-8')
        print(f"Encrypted bytes length: {len(encrypted_bytes)}")
        print(f"First 20 bytes: {encrypted_bytes[:20]}")
        
        # 解密
        decrypted_bytes = fernet.decrypt(encrypted_bytes)
        print(f"Decrypted bytes length: {len(decrypted_bytes)}")
        print(f"Decrypted bytes: {decrypted_bytes}")
        
        # 返回解密后的字符串
        decrypted_str = decrypted_bytes.decode('utf-8')
        print(f"Decrypted string: {decrypted_str}")
        return decrypted_str
    except Exception as e:
        print(f"Decryption error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None

def run_decrypt():
    settings = QSettings("AiMedia", "ai-media")
    openid = settings.value("openid")
    print("openid:", openid)
    
    if not openid:
        print("Error: No openid found")
        return None
        
    encrypted_text = get_gml_key()
    print("encrypted_text:", encrypted_text)
    
    if not encrypted_text:
        print("Error: No encrypted text received")
        return None
        
    if encrypted_text is False:
        print("Error: Token usage exceeded limit")
        return None
        
    try:
        key = generate_key_from_string(openid)
        print("Generated key:", key)
        fernet = initialize_fernet(key)
        dec_key = decrypt_string(fernet, encrypted_text)
        print("key:", key.decode('utf-8'), "dec_key:", dec_key)
        return dec_key
    except Exception as e:
        print(f"Error during decryption: {str(e)}")
        return None