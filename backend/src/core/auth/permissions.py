"""
权限验证服务模块

提供权限验证相关的核心功能
"""
from typing import List, Optional, Set
from functools import wraps

from fastapi import HTTPException, status
from api.core.base.models import UserBase as UserOut, PermissionEnum

class PermissionService:
    """权限验证服务类"""
    
    @staticmethod
    def has_permission(user: UserOut, required_permission: PermissionEnum) -> bool:
        """
        检查用户是否具有指定权限
        
        Args:
            user: 用户信息
            required_permission: 所需权限
            
        Returns:
            bool: 是否具有权限
        """
        return required_permission in user.permissions

    @staticmethod
    def has_any_permission(user: UserOut, required_permissions: List[PermissionEnum]) -> bool:
        """
        检查用户是否具有指定权限中的任意一个
        
        Args:
            user: 用户信息
            required_permissions: 所需权限列表
            
        Returns:
            bool: 是否具有权限
        """
        return any(perm in user.permissions for perm in required_permissions)

    @staticmethod
    def has_all_permissions(user: UserOut, required_permissions: List[PermissionEnum]) -> bool:
        """
        检查用户是否具有指定的所有权限
        
        Args:
            user: 用户信息
            required_permissions: 所需权限列表
            
        Returns:
            bool: 是否具有所有权限
        """
        return all(perm in user.permissions for perm in required_permissions)

    @staticmethod
    def get_user_permissions(user: UserOut) -> Set[PermissionEnum]:
        """
        获取用户的所有权限
        
        Args:
            user: 用户信息
            
        Returns:
            Set[PermissionEnum]: 用户权限集合
        """
        return set(user.permissions)

# 创建权限服务实例
permission_service = PermissionService()

def require_permission(permission: PermissionEnum):
    """
    权限要求装饰器
    
    Args:
        permission: 所需权限
        
    Returns:
        callable: 装饰器函数
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: UserOut, **kwargs):
            if not permission_service.has_permission(current_user, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"权限不足: 需要 {permission} 权限"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

def require_any_permission(permissions: List[PermissionEnum]):
    """
    要求任意权限装饰器
    
    Args:
        permissions: 所需权限列表
        
    Returns:
        callable: 装饰器函数
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: UserOut, **kwargs):
            if not permission_service.has_any_permission(current_user, permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"权限不足: 需要以下权限之一 {', '.join(p.value for p in permissions)}"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

def require_all_permissions(permissions: List[PermissionEnum]):
    """
    要求所有权限装饰器
    
    Args:
        permissions: 所需权限列表
        
    Returns:
        callable: 装饰器函数
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: UserOut, **kwargs):
            if not permission_service.has_all_permissions(current_user, permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"权限不足: 需要以下所有权限 {', '.join(p.value for p in permissions)}"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator 