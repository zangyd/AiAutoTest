from src.api.base import StatusEnum

# 测试用户数据
test_user_data = {
    "username": "test_user",
    "email": "test@example.com",
    "password": "password123",
    "department": "技术部",
    "position": "工程师",
    "status": StatusEnum.ACTIVE
}

# 测试管理员数据
test_admin_data = {
    "username": "admin_user",
    "email": "admin@example.com",
    "password": "admin123",
    "department": "管理部",
    "position": "管理员",
    "status": StatusEnum.ACTIVE
}

# 无效用户数据
invalid_user_data = {
    "username": "u",  # 用户名太短
    "email": "invalid_email",  # 无效邮箱
    "password": "123",  # 密码太短
    "department": "",  # 空部门
    "position": "开发工程师",
    "status": "invalid_status"  # 无效状态
}

# 更新用户数据
update_user_data = {
    "department": "测试部",
    "position": "测试工程师",
    "status": StatusEnum.ACTIVE
}

# 搜索测试数据
search_test_data = [
    "test_user",
    "技术部",
    "工程师"
]

# 排序测试数据
sort_test_data = [
    ("username", "asc"),
    ("created_at", "desc"),
    ("department", "asc")
]

# 分页测试数据
pagination_test_data = [
    {"page": 1, "size": 10},
    {"page": 2, "size": 5},
    {"page": 1, "size": 20}
] 