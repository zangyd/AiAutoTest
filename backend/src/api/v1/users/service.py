"""
用户相关的业务逻辑
"""
from typing import List, Optional
from fastapi import HTTPException, status

from .schemas import UserCreate, UserUpdate, UserOut
from ....core.base.models import StatusEnum
from ....core.base.schemas import PageModel, PaginationParams, QueryParams

# 模拟数据库
users_db = {
    1: UserOut(
        id=1,
        username="admin",
        email="admin@example.com",
        department="技术部",
        position="管理员",
        status=StatusEnum.ACTIVE,
        permissions=["admin", "user_view", "user_manage"]
    ),
    2: UserOut(
        id=2,
        username="test_user",
        email="test@example.com",
        department="技术部",
        position="工程师",
        status=StatusEnum.ACTIVE,
        permissions=["user_view"]
    )
}

async def create_user(user: UserCreate, current_user: UserOut) -> UserOut:
    """
    创建用户
    
    Args:
        user: 用户创建信息
        current_user: 当前用户
        
    Returns:
        UserOut: 创建成功的用户信息
        
    Raises:
        HTTPException: 当权限不足或用户名已存在时
    """
    # 检查权限
    if "admin" not in current_user.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    # 检查用户名是否已存在
    if any(u.username == user.username for u in users_db.values()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # 创建新用户
    new_user_id = max(users_db.keys()) + 1
    new_user = UserOut(
        id=new_user_id,
        username=user.username,
        email=user.email,
        department=user.department,
        position=user.position,
        status=StatusEnum.ACTIVE,
        permissions=["user_view"]
    )
    users_db[new_user_id] = new_user
    
    return new_user

async def get_users(
    pagination: PaginationParams,
    query: QueryParams,
    current_user: UserOut
) -> PageModel[UserOut]:
    """
    获取用户列表
    
    Args:
        pagination: 分页参数
        query: 查询参数
        current_user: 当前用户
        
    Returns:
        PageModel[UserOut]: 分页后的用户列表
        
    Raises:
        HTTPException: 当权限不足时
    """
    # 检查权限
    if "user_view" not in current_user.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    # 过滤和分页
    users = list(users_db.values())
    if query.search:
        users = [
            u for u in users
            if query.search.lower() in u.username.lower() or
               query.search.lower() in u.department.lower() or
               query.search.lower() in u.position.lower()
        ]
    
    # 计算分页
    total = len(users)
    start = (pagination.page - 1) * pagination.size
    end = start + pagination.size
    items = users[start:end]
    
    return PageModel(
        items=items,
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=(total + pagination.size - 1) // pagination.size
    )

async def get_user(user_id: int, current_user: UserOut) -> UserOut:
    """
    获取用户详情
    
    Args:
        user_id: 用户ID
        current_user: 当前用户
        
    Returns:
        UserOut: 用户详细信息
        
    Raises:
        HTTPException: 当权限不足或用户不存在时
    """
    # 检查权限
    if "user_view" not in current_user.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return users_db[user_id]

async def update_user(
    user_id: int,
    user: UserUpdate,
    current_user: UserOut
) -> UserOut:
    """
    更新用户信息
    
    Args:
        user_id: 用户ID
        user: 用户更新信息
        current_user: 当前用户
        
    Returns:
        UserOut: 更新后的用户信息
        
    Raises:
        HTTPException: 当权限不足或用户不存在时
    """
    # 检查权限
    if "user_manage" not in current_user.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # 更新用户信息
    current_user_data = users_db[user_id]
    update_data = user.dict(exclude_unset=True)
    
    updated_user = UserOut(
        **{
            **current_user_data.dict(),
            **update_data
        }
    )
    users_db[user_id] = updated_user
    
    return updated_user

async def delete_user(user_id: int, current_user: UserOut) -> None:
    """
    删除用户
    
    Args:
        user_id: 用户ID
        current_user: 当前用户
        
    Raises:
        HTTPException: 当权限不足或用户不存在时
    """
    # 检查权限
    if "admin" not in current_user.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # 删除用户
    del users_db[user_id] 