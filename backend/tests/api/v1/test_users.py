import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from typing import Dict, Any
from tests.config import TEST_USERS, API_CONFIG

from api.base import StatusEnum
from api.models import UserCreate, UserUpdate, UserOut
from core.auth.jwt import jwt_handler

# 测试数据
test_user_data = {
    "username": "new_test_user",
    "email": "newtest@example.com",
    "department": "技术部",
    "position": "工程师",
    "password": "Test123456!"
}

@pytest.fixture
def admin_token() -> str:
    """生成管理员令牌"""
    return jwt_handler.create_token({"sub": "admin"})

@pytest.fixture
def user_token() -> str:
    """生成普通用户令牌"""
    return jwt_handler.create_token({"sub": "test_user"})

@pytest.fixture
def admin_headers(admin_token: str) -> Dict[str, str]:
    """管理员请求头"""
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture
def user_headers(user_token: str) -> Dict[str, str]:
    """普通用户请求头"""
    return {"Authorization": f"Bearer {user_token}"}

class TestUserAPI:
    """用户API测试类"""
    
    def test_create_user_success(self, client: TestClient, admin_headers: Dict[str, str]):
        """测试成功创建用户"""
        response = client.post(
            "/api/v1/users",
            json=test_user_data,
            headers=admin_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["code"] == 201
        assert data["message"] == "用户创建成功"
        assert data["data"]["username"] == test_user_data["username"]

    @pytest.mark.parametrize("invalid_data", [
        {"username": "te"},  # 用户名太短
        {"username": "test_user", "email": "invalid_email"},  # 无效的邮箱
        {"username": "test_user", "email": "test@example.com", "password": "short"},  # 密码太短
    ])
    def test_create_user_invalid_data(self, client: TestClient, admin_headers: Dict[str, str], invalid_data: dict):
        """测试创建用户时的无效数据处理"""
        response = client.post(
            "/api/v1/users",
            json=invalid_data,
            headers=admin_headers
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_get_users_success(self, client: TestClient, user_headers: Dict[str, str]):
        """测试成功获取用户列表"""
        response = client.get(
            "/api/v1/users",
            headers=user_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "data" in data
        assert "total" in data["data"]
        assert "items" in data["data"]

    def test_get_users_with_pagination(self, client: TestClient, user_headers: Dict[str, str]):
        """测试用户列表分页"""
        response = client.get("/api/v1/users?page=1&size=10", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "data" in data
        assert len(data["data"]["items"]) <= 10

    def test_get_user_success(self, client: TestClient, admin_headers: Dict[str, str]):
        """测试成功获取单个用户"""
        # 获取已存在的测试用户详情
        response = client.get(
            "/api/v1/users/2",  # test_user的ID
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["username"] == "test_user"

    def test_get_user_not_found(self, client: TestClient, user_headers: Dict[str, str]):
        """测试获取不存在的用户"""
        response = client.get("/api/v1/users/999", headers=user_headers)
        assert response.status_code == 404
        data = response.json()
        assert data["code"] == 404

    def test_update_user_success(self, client: TestClient, admin_headers: Dict[str, str]):
        """测试成功更新用户"""
        update_data = {
            "department": "研发部",
            "position": "高级工程师"
        }
        response = client.put(
            "/api/v1/users/2",  # test_user的ID
            json=update_data,
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["department"] == update_data["department"]
        assert data["data"]["position"] == update_data["position"]

    def test_update_user_invalid_data(self, client: TestClient, admin_headers: Dict[str, str]):
        """测试更新用户时的无效数据处理"""
        invalid_data = {
            "email": "invalid_email",
            "status": "invalid_status"
        }
        response = client.put("/api/v1/users/2", json=invalid_data, headers=admin_headers)
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_delete_user_success(self, client: TestClient, admin_headers: Dict[str, str]):
        """测试成功删除用户"""
        # 先创建一个新用户
        create_response = client.post(
            "/api/v1/users",
            json=test_user_data,
            headers=admin_headers
        )
        user_id = create_response.json()["data"]["id"]
        
        # 删除用户
        response = client.delete(
            f"/api/v1/users/{user_id}",
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["message"] == "用户删除成功"

    def test_delete_user_not_found(self, client: TestClient, admin_headers: Dict[str, str]):
        """测试删除不存在的用户"""
        response = client.delete("/api/v1/users/999", headers=admin_headers)
        assert response.status_code == 404
        data = response.json()
        assert data["code"] == 404

    @pytest.mark.parametrize("search_query", [
        "test_user",
        "技术部",
        "工程师"
    ])
    def test_search_users(self, client: TestClient, user_headers: Dict[str, str], search_query: str):
        """测试用户搜索功能"""
        response = client.get(f"/api/v1/users?search={search_query}", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "data" in data
        assert "items" in data["data"]

    def test_unauthorized_access(self, client: TestClient):
        """测试未授权访问"""
        response = client.get("/api/v1/users")
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_forbidden_access(self, client: TestClient, user_headers: Dict[str, str]):
        """测试权限不足访问"""
        response = client.post(
            "/api/v1/users",
            json=test_user_data,
            headers=user_headers
        )
        assert response.status_code == 403
        data = response.json()
        assert "detail" in data 