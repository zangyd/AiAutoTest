"""
用户管理相关的路由处理
"""
from typing import List
from fastapi import APIRouter, Depends, Query

from .schemas import UserCreate, UserUpdate, UserOut
from .service import (
    create_user,
    get_users,
    get_user,
    update_user,
    delete_user
)
from ....core.base.schemas import (
    Response,
    PageModel,
    PaginationParams,
    QueryParams
)
from ....core.auth import get_current_user

router = APIRouter(prefix="/users", tags=["用户管理"])

@router.post("", response_model=Response[UserOut])
async def create_user_route(
    user: UserCreate,
    current_user: UserOut = Depends(get_current_user)
) -> Response[UserOut]:
    """
    创建用户
    
    Args:
        user: 用户创建信息
        current_user: 当前用户(通过token获取)
        
    Returns:
        Response[UserOut]: 创建成功的用户信息
    """
    result = await create_user(user, current_user)
    return Response(
        code=200,
        message="创建成功",
        data=result
    )

@router.get("", response_model=Response[PageModel[UserOut]])
async def get_users_route(
    page: int = Query(1, description="页码", ge=1),
    size: int = Query(10, description="每页数量", ge=1, le=100),
    search: str = Query(None, description="搜索关键词"),
    current_user: UserOut = Depends(get_current_user)
) -> Response[PageModel[UserOut]]:
    """
    获取用户列表
    
    Args:
        page: 页码
        size: 每页数量
        search: 搜索关键词
        current_user: 当前用户(通过token获取)
        
    Returns:
        Response[PageModel[UserOut]]: 分页后的用户列表
    """
    pagination = PaginationParams(page=page, size=size)
    query = QueryParams(search=search)
    result = await get_users(pagination, query, current_user)
    return Response(
        code=200,
        message="获取成功",
        data=result
    )

@router.get("/{user_id}", response_model=Response[UserOut])
async def get_user_route(
    user_id: int,
    current_user: UserOut = Depends(get_current_user)
) -> Response[UserOut]:
    """
    获取用户详情
    
    Args:
        user_id: 用户ID
        current_user: 当前用户(通过token获取)
        
    Returns:
        Response[UserOut]: 用户详细信息
    """
    result = await get_user(user_id, current_user)
    return Response(
        code=200,
        message="获取成功",
        data=result
    )

@router.put("/{user_id}", response_model=Response[UserOut])
async def update_user_route(
    user_id: int,
    user: UserUpdate,
    current_user: UserOut = Depends(get_current_user)
) -> Response[UserOut]:
    """
    更新用户信息
    
    Args:
        user_id: 用户ID
        user: 用户更新信息
        current_user: 当前用户(通过token获取)
        
    Returns:
        Response[UserOut]: 更新后的用户信息
    """
    result = await update_user(user_id, user, current_user)
    return Response(
        code=200,
        message="更新成功",
        data=result
    )

@router.delete("/{user_id}", response_model=Response)
async def delete_user_route(
    user_id: int,
    current_user: UserOut = Depends(get_current_user)
) -> Response:
    """
    删除用户
    
    Args:
        user_id: 用户ID
        current_user: 当前用户(通过token获取)
        
    Returns:
        Response: 删除结果
    """
    await delete_user(user_id, current_user)
    return Response(
        code=200,
        message="删除成功"
    ) 