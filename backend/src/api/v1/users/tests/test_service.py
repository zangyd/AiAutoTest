"""
用户服务层测试用例
"""
import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any

from ..schemas import UserCreate, UserUpdate, UserOut
from ..service import create_user, get_users, get_user, update_user, delete_user
from ..exceptions import (
    UserNotFound,
    UserAlreadyExists,
    InsufficientPermissions,
    UserStatusError
)
from ...base import StatusEnum, PaginationParams, QueryParams

# 测试数据
test_admin = UserOut(
    id=1,
    username="admin",
    email="admin@example.com",
    department="技术部",
    position="管理员",
    status=StatusEnum.ACTIVE,
    permissions=["admin", "user_view", "user_manage"]
)

test_user = UserOut(
    id=2,
    username="test_user",
    email="test@example.com",
    department="技术部",
    position="工程师",
    status=StatusEnum.ACTIVE,
    permissions=["user_view"]
)

@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_users_db(mocker):
    """Mock用户数据库"""
    mock_db = {
        1: test_admin,
        2: test_user
    }
    mocker.patch("api.v1.users.service.users_db", mock_db)
    return mock_db

@pytest.mark.asyncio
async def test_create_user_success(mock_users_db):
    """测试成功创建用户"""
    new_user_data = UserCreate(
        username="new_user",
        email="new@example.com",
        department="技术部",
        position="测试工程师"
    )
    
    result = await create_user(new_user_data, test_admin)
    
    assert result.username == new_user_data.username
    assert result.email == new_user_data.email
    assert result.status == StatusEnum.ACTIVE
    assert "user_view" in result.permissions

@pytest.mark.asyncio
async def test_create_user_already_exists(mock_users_db):
    """测试创建已存在的用户"""
    existing_user_data = UserCreate(
        username="admin",
        email="new@example.com",
        department="技术部",
        position="测试工程师"
    )
    
    with pytest.raises(UserAlreadyExists) as exc_info:
        await create_user(existing_user_data, test_admin)
    
    assert exc_info.value.code == 40001
    assert "admin" in exc_info.value.message

@pytest.mark.asyncio
async def test_create_user_insufficient_permissions(mock_users_db):
    """测试无权限创建用户"""
    new_user_data = UserCreate(
        username="new_user",
        email="new@example.com",
        department="技术部",
        position="测试工程师"
    )
    
    with pytest.raises(InsufficientPermissions) as exc_info:
        await create_user(new_user_data, test_user)
    
    assert exc_info.value.code == 40301
    assert "admin" in exc_info.value.details["required_permissions"]

@pytest.mark.asyncio
async def test_get_users_success(mock_users_db):
    """测试成功获取用户列表"""
    pagination = PaginationParams(page=1, size=10)
    query = QueryParams(search=None)
    
    result = await get_users(pagination, query, test_admin)
    
    assert result.total == 2
    assert len(result.items) == 2
    assert result.page == 1
    assert result.size == 10

@pytest.mark.asyncio
async def test_get_users_with_search(mock_users_db):
    """测试搜索用户列表"""
    pagination = PaginationParams(page=1, size=10)
    query = QueryParams(search="admin")
    
    result = await get_users(pagination, query, test_admin)
    
    assert result.total == 1
    assert len(result.items) == 1
    assert result.items[0].username == "admin"

@pytest.mark.asyncio
async def test_get_users_insufficient_permissions(mock_users_db):
    """测试无权限获取用户列表"""
    no_permission_user = UserOut(
        id=3,
        username="no_permission",
        email="no@example.com",
        department="技术部",
        position="访客",
        status=StatusEnum.ACTIVE,
        permissions=[]
    )
    
    pagination = PaginationParams(page=1, size=10)
    query = QueryParams(search=None)
    
    with pytest.raises(InsufficientPermissions) as exc_info:
        await get_users(pagination, query, no_permission_user)
    
    assert exc_info.value.code == 40301
    assert "user_view" in exc_info.value.details["required_permissions"]

@pytest.mark.asyncio
async def test_get_user_success(mock_users_db):
    """测试成功获取用户详情"""
    result = await get_user(1, test_admin)
    
    assert result.id == 1
    assert result.username == "admin"

@pytest.mark.asyncio
async def test_get_user_not_found(mock_users_db):
    """测试获取不存在的用户"""
    with pytest.raises(UserNotFound) as exc_info:
        await get_user(999, test_admin)
    
    assert exc_info.value.code == 40401
    assert "999" in exc_info.value.message

@pytest.mark.asyncio
async def test_update_user_success(mock_users_db):
    """测试成功更新用户"""
    update_data = UserUpdate(
        email="updated@example.com",
        department="研发部",
        position="高级工程师"
    )
    
    result = await update_user(2, update_data, test_admin)
    
    assert result.email == update_data.email
    assert result.department == update_data.department
    assert result.position == update_data.position

@pytest.mark.asyncio
async def test_update_user_not_found(mock_users_db):
    """测试更新不存在的用户"""
    update_data = UserUpdate(
        email="updated@example.com"
    )
    
    with pytest.raises(UserNotFound) as exc_info:
        await update_user(999, update_data, test_admin)
    
    assert exc_info.value.code == 40401

@pytest.mark.asyncio
async def test_delete_user_success(mock_users_db):
    """测试成功删除用户"""
    await delete_user(2, test_admin)
    
    with pytest.raises(UserNotFound):
        await get_user(2, test_admin)

@pytest.mark.asyncio
async def test_delete_user_not_found(mock_users_db):
    """测试删除不存在的用户"""
    with pytest.raises(UserNotFound) as exc_info:
        await delete_user(999, test_admin)
    
    assert exc_info.value.code == 40401 