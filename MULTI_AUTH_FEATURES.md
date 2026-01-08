# 多方式认证系统说明

## 功能概述
本项目现在支持多种用户认证方式：
1. 微信扫码登录（原有的功能）
2. 邮箱注册与登录（新增功能）

## API 接口

### 邮箱注册
- **端点**: `POST /api/user/register/`
- **请求参数**:
  ```json
  {
    "email": "user@example.com",
    "password": "password123",
    "nickname": "用户名"
  }
  ```
- **响应示例**:
  ```json
  {
    "code": 0,
    "message": "注册成功",
    "result": {
      "access": "...",
      "refresh": "...",
      "user_info": {...}
    }
  }
  ```

### 邮箱登录
- **端点**: `POST /api/user/login/`
- **请求参数**:
  ```json
  {
    "username": "user@example.com", // 可以是邮箱、手机号或open_id
    "password": "password123"
  }
  ```
- **响应示例**:
  ```json
  {
    "code": 0,
    "message": "登录成功",
    "result": {
      "access": "...",
      "refresh": "...",
      "user_info": {...}
    }
  }
  ```

### 通用认证接口
- **端点**: `POST /api/user/auth/`
- **请求参数**:
  ```json
  {
    "action": "register", // 或 "login"
    "email": "user@example.com",
    "password": "password123",
    "nickname": "用户名"
  }
  ```

## 认证后端
实现了 `MultiAuthBackend` 支持以下登录方式：
- 邮箱登录
- 手机号登录
- open_id 登录（微信登录）

## PySide 应用更新
- 登录窗口现在支持微信扫码和邮箱登录两种方式
- 用户可以在登录界面切换认证方式
- 邮箱登录支持注册和登录功能

## 数据库变更
- 用户模型现在使用 email 作为 USERNAME_FIELD
- open_id 字段改为可空，支持非微信用户
- email 和 open_id 都建立了数据库索引