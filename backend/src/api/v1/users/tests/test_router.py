"""
用户路由测试用例
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from ....main import app
from ..schemas import UserOut
from ....core.base.models import StatusEnum
from ....core.base.schemas import Response, PageModel

client = TestClient(app)

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

@pytest.fixture
def mock_get_current_user():
    """Mock当前用户"""
    with patch("api.v1.users.router.get_current_user") as mock:
        mock.return_value = test_admin
        yield mock

def test_create_user_success(mock_get_current_user):
    """测试成功创建用户"""
    user_data = {
        "username": "new_user",
        "email": "new@example.com",
        "department": "技术部",
        "position": "测试工程师"
    }
    
    response = client.post("/api/v1/users", json=user_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "创建成功"
    assert data["data"]["username"] == user_data["username"]
    assert data["data"]["email"] == user_data["email"]
    assert data["data"]["status"] == StatusEnum.ACTIVE
    assert "user_view" in data["data"]["permissions"]

def test_create_user_invalid_data(mock_get_current_user):
    """测试创建用户数据无效"""
    invalid_data = {
        "username": "",  # 无效的用户名
        "email": "invalid_email",  # 无效的邮箱
        "department": "技术部",
        "position": "测试工程师"
    }
    
    response = client.post("/api/v1/users", json=invalid_data)
    assert response.status_code == 422  # FastAPI的验证错误状态码

def test_get_users_success(mock_get_current_user):
    """测试成功获取用户列表"""
    response = client.get("/api/v1/users?page=1&size=10")
    assert response.status_code == 200
    
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "获取成功"
    assert "total" in data["data"]
    assert "items" in data["data"]
    assert "page" in data["data"]
    assert "size" in data["data"]

def test_get_users_with_search(mock_get_current_user):
    """测试搜索用户列表"""
    response = client.get("/api/v1/users?page=1&size=10&search=admin")
    assert response.status_code == 200
    
    data = response.json()
    assert data["code"] == 200
    assert len(data["data"]["items"]) > 0
    assert "admin" in data["data"]["items"][0]["username"]

def test_get_user_success(mock_get_current_user):
    """测试成功获取用户详情"""
    response = client.get("/api/v1/users/1")
    assert response.status_code == 200
    
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "获取成功"
    assert data["data"]["id"] == 1
    assert data["data"]["username"] == "admin"

def test_get_user_not_found(mock_get_current_user):
    """测试获取不存在的用户"""
    response = client.get("/api/v1/users/999")
    assert response.status_code == 404
    
    data = response.json()
    assert data["code"] == 40401
    assert "999" in data["message"]

def test_update_user_success(mock_get_current_user):
    """测试成功更新用户"""
    update_data = {
        "email": "updated@example.com",
        "department": "研发部",
        "position": "高级工程师"
    }
    
    response = client.put("/api/v1/users/2", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "更新成功"
    assert data["data"]["email"] == update_data["email"]
    assert data["data"]["department"] == update_data["department"]
    assert data["data"]["position"] == update_data["position"]

def test_update_user_not_found(mock_get_current_user):
    """测试更新不存在的用户"""
    update_data = {
        "email": "updated@example.com"
    }
    
    response = client.put("/api/v1/users/999", json=update_data)
    assert response.status_code == 404
    
    data = response.json()
    assert data["code"] == 40401

def test_delete_user_success(mock_get_current_user):
    """测试成功删除用户"""
    response = client.delete("/api/v1/users/2")
    assert response.status_code == 200
    
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "删除成功"

def test_delete_user_not_found(mock_get_current_user):
    """测试删除不存在的用户"""
    response = client.delete("/api/v1/users/999")
    assert response.status_code == 404
    
    data = response.json()
    assert data["code"] == 40401

def test_unauthorized_access():
    """测试未授权访问"""
    response = client.get("/api/v1/users")
    assert response.status_code == 401
    
    data = response.json()
    assert data["code"] == 40101 