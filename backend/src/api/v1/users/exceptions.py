"""
用户管理模块的自定义异常类
"""
from fastapi import status
from ...base.exceptions import BaseAPIException


class UserException(BaseAPIException):
    """用户模块基础异常类"""
    pass


class UserNotFound(UserException):
    """用户不存在异常"""
    def __init__(self, user_id: int):
        self.status_code = status.HTTP_404_NOT_FOUND
        self.code = 40401
        self.message = f"用户[{user_id}]不存在"
        self.details = {
            "user_id": user_id
        }


class UserAlreadyExists(UserException):
    """用户已存在异常"""
    def __init__(self, username: str):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.code = 40001
        self.message = f"用户名[{username}]已存在"
        self.details = {
            "username": username
        }


class InvalidPassword(UserException):
    """密码无效异常"""
    def __init__(self):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.code = 40002
        self.message = "密码不符合要求"
        self.details = {
            "rules": {
                "min_length": 8,
                "max_length": 20,
                "require_upper": True,
                "require_lower": True,
                "require_digit": True,
                "require_special": True
            }
        }


class UserStatusError(UserException):
    """用户状态异常"""
    def __init__(self, user_id: int, current_status: str, required_status: str):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.code = 40003
        self.message = f"用户[{user_id}]状态错误"
        self.details = {
            "user_id": user_id,
            "current_status": current_status,
            "required_status": required_status
        }


class InsufficientPermissions(UserException):
    """权限不足异常"""
    def __init__(self, user_id: int, required_permissions: list[str]):
        self.status_code = status.HTTP_403_FORBIDDEN
        self.code = 40301
        self.message = "权限不足"
        self.details = {
            "user_id": user_id,
            "required_permissions": required_permissions
        }


class InvalidUserData(UserException):
    """用户数据无效异常"""
    def __init__(self, field: str, reason: str):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.code = 40004
        self.message = f"用户数据无效: {field}"
        self.details = {
            "field": field,
            "reason": reason
        }


class UserOperationFailed(UserException):
    """用户操作失败异常"""
    def __init__(self, operation: str, reason: str):
        self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        self.code = 50001
        self.message = f"用户操作[{operation}]失败"
        self.details = {
            "operation": operation,
            "reason": reason
        }


class UserLocked(UserException):
    """用户被锁定异常"""
    def __init__(self, user_id: int, lock_reason: str, unlock_time: str = None):
        self.status_code = status.HTTP_403_FORBIDDEN
        self.code = 40302
        self.message = f"用户[{user_id}]已被锁定"
        self.details = {
            "user_id": user_id,
            "lock_reason": lock_reason,
            "unlock_time": unlock_time
        }


class InvalidToken(UserException):
    """Token无效异常"""
    def __init__(self, reason: str):
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.code = 40101
        self.message = "Token无效"
        self.details = {
            "reason": reason
        }


class TokenExpired(UserException):
    """Token过期异常"""
    def __init__(self, expired_at: str):
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.code = 40102
        self.message = "Token已过期"
        self.details = {
            "expired_at": expired_at
        } 