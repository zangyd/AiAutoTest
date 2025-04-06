from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, status

from ..base import (
    ResponseModel,
    PageModel,
    ErrorModel,
    PaginationParams,
    QueryParams,
    StatusEnum
)
from ..deps import get_current_user, check_permissions
from ..models import UserBase, UserCreate, UserUpdate, UserOut, PermissionEnum
from ...core.auth.dependencies import get_current_active_user
from ...core.auth.permissions import require_permission, require_any_permission
from ...core.logging import logger, log_method_call, log_data_change

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

router = APIRouter(prefix="/api/v1/users", tags=["用户管理"])

@router.post(
    "",
    response_model=ResponseModel[UserOut],
    summary="创建用户",
    description="创建新用户，需要user:create权限",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "创建成功"},
        422: {"model": ErrorModel, "description": "请求参数错误"},
        401: {"model": ErrorModel, "description": "未授权"},
        403: {"model": ErrorModel, "description": "权限不足"},
    }
)
@require_permission(PermissionEnum.USER_CREATE)
@log_method_call("创建用户")
@log_data_change(UserOut, "create")
async def create_user(
    user: UserCreate,
    current_user: UserOut = Depends(get_current_active_user)
) -> ResponseModel[UserOut]:
    """
    创建用户接口
    
    Args:
        user: 用户创建信息
        
    Returns:
        ResponseModel[UserOut]: 创建成功的用户信息
        
    Raises:
        HTTPException: 当认证失败或权限不足时
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
    
    return ResponseModel[UserOut](
        code=201,
        message="用户创建成功",
        data=new_user
    )

@router.get(
    "",
    response_model=ResponseModel[PageModel[UserOut]],
    summary="获取用户列表",
    description="获取用户列表，需要user:read权限",
    responses={
        200: {"description": "获取成功"},
        401: {"model": ErrorModel, "description": "未授权"},
        403: {"model": ErrorModel, "description": "权限不足"},
    }
)
@require_permission(PermissionEnum.USER_READ)
@log_method_call("获取用户列表")
async def get_users(
    pagination: PaginationParams = Depends(),
    query: QueryParams = Depends(),
    current_user: UserOut = Depends(get_current_active_user)
) -> ResponseModel[PageModel[UserOut]]:
    """
    获取用户列表接口
    
    Args:
        pagination: 分页参数
        query: 查询参数
        current_user: 当前用户
        
    Returns:
        ResponseModel[PageModel[UserOut]]: 分页后的用户列表
        
    Raises:
        HTTPException: 当认证失败或权限不足时
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
    
    return ResponseModel[PageModel[UserOut]](
        code=200,
        message="获取用户列表成功",
        data=PageModel(
            items=items,
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=(total + pagination.size - 1) // pagination.size
        )
    )

@router.get(
    "/{user_id}",
    response_model=ResponseModel[UserOut],
    summary="获取用户详情",
    description="获取指定用户的详细信息，需要user:read权限",
    responses={
        200: {"description": "获取成功"},
        401: {"model": ErrorModel, "description": "未授权"},
        403: {"model": ErrorModel, "description": "权限不足"},
        404: {"model": ErrorModel, "description": "用户不存在"},
    }
)
@require_permission(PermissionEnum.USER_READ)
@log_method_call("获取用户详情")
async def get_user(
    user_id: int = Path(..., description="用户ID"),
    current_user: UserOut = Depends(get_current_active_user)
) -> ResponseModel[UserOut]:
    """
    获取用户详情接口
    
    Args:
        user_id: 用户ID
        current_user: 当前用户
        
    Returns:
        ResponseModel[UserOut]: 用户详细信息
        
    Raises:
        HTTPException: 当认证失败、权限不足或用户不存在时
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
    
    return ResponseModel[UserOut](
        code=200,
        message="获取用户详情成功",
        data=users_db[user_id]
    )

@router.put(
    "/{user_id}",
    response_model=ResponseModel[UserOut],
    summary="更新用户信息",
    description="更新指定用户的信息，需要user:update权限",
    responses={
        200: {"description": "更新成功"},
        422: {"model": ErrorModel, "description": "请求参数错误"},
        401: {"model": ErrorModel, "description": "未授权"},
        403: {"model": ErrorModel, "description": "权限不足"},
        404: {"model": ErrorModel, "description": "用户不存在"},
    }
)
@require_permission(PermissionEnum.USER_UPDATE)
@log_method_call("更新用户信息")
@log_data_change(UserOut, "update")
async def update_user(
    user_id: int = Path(..., description="用户ID"),
    user: UserUpdate = Body(..., description="用户更新信息"),
    current_user: UserOut = Depends(get_current_active_user)
) -> ResponseModel[UserOut]:
    """
    更新用户信息接口
    
    Args:
        user_id: 用户ID
        user: 用户更新信息
        current_user: 当前用户
        
    Returns:
        ResponseModel[UserOut]: 更新后的用户信息
        
    Raises:
        HTTPException: 当认证失败、权限不足或用户不存在时
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
    
    # 更新用户信息
    current_user_data = users_db[user_id]
    updated_user = UserOut(
        id=user_id,
        username=current_user_data.username,
        email=user.email or current_user_data.email,
        department=user.department or current_user_data.department,
        position=user.position or current_user_data.position,
        status=user.status or current_user_data.status,
        permissions=current_user_data.permissions
    )
    users_db[user_id] = updated_user
    
    return ResponseModel[UserOut](
        code=200,
        message="用户更新成功",
        data=updated_user
    )

@router.delete(
    "/{user_id}",
    response_model=ResponseModel[None],
    summary="删除用户",
    description="删除指定用户，需要user:delete权限",
    responses={
        200: {"description": "删除成功"},
        401: {"model": ErrorModel, "description": "未授权"},
        403: {"model": ErrorModel, "description": "权限不足"},
        404: {"model": ErrorModel, "description": "用户不存在"},
    }
)
@require_permission(PermissionEnum.USER_DELETE)
@log_method_call("删除用户")
@log_data_change(UserOut, "delete")
async def delete_user(
    user_id: int = Path(..., description="用户ID"),
    current_user: UserOut = Depends(get_current_active_user)
) -> ResponseModel[None]:
    """
    删除用户接口
    
    Args:
        user_id: 用户ID
        current_user: 当前用户
        
    Returns:
        ResponseModel[None]: 删除成功的响应
        
    Raises:
        HTTPException: 当认证失败、权限不足或用户不存在时
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
    
    # 不允许删除自己
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )
    
    del users_db[user_id]
    
    return ResponseModel[None](
        code=200,
        message="用户删除成功"
    ) 