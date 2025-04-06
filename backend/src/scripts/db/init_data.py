"""
初始化数据脚本
"""
import os
import sys
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from backend.src.core.database import SessionLocal
from backend.src.api.models.user import User, Role, Permission, Department
from backend.src.core.security import get_password_hash

def init_permissions(db):
    """初始化权限"""
    permissions = [
        {"name": "用户管理", "code": "user:manage", "description": "用户的增删改查"},
        {"name": "角色管理", "code": "role:manage", "description": "角色的增删改查"},
        {"name": "权限管理", "code": "permission:manage", "description": "权限的增删改查"},
        {"name": "部门管理", "code": "department:manage", "description": "部门的增删改查"},
        {"name": "测试用例管理", "code": "testcase:manage", "description": "测试用例的增删改查"},
        {"name": "测试计划管理", "code": "testplan:manage", "description": "测试计划的增删改查"},
        {"name": "测试执行", "code": "test:execute", "description": "执行测试"},
        {"name": "测试报告管理", "code": "report:manage", "description": "测试报告的查看和导出"},
    ]
    
    for perm_data in permissions:
        perm = Permission(**perm_data)
        db.add(perm)
    
    db.commit()
    return permissions

def init_roles(db):
    """初始化角色"""
    # 获取所有权限
    all_permissions = db.query(Permission).all()
    
    # 创建超级管理员角色
    admin_role = Role(
        name="超级管理员",
        description="系统超级管理员，拥有所有权限",
        permissions=all_permissions
    )
    db.add(admin_role)
    
    # 创建测试工程师角色
    test_permissions = db.query(Permission).filter(
        Permission.code.in_([
            "testcase:manage",
            "testplan:manage",
            "test:execute",
            "report:manage"
        ])
    ).all()
    
    test_role = Role(
        name="测试工程师",
        description="测试工程师，负责测试用例管理和执行",
        permissions=test_permissions
    )
    db.add(test_role)
    
    db.commit()
    return [admin_role, test_role]

def init_departments(db):
    """初始化部门"""
    # 创建测试部门
    test_dept = Department(
        name="测试部",
        description="负责系统测试和质量保证"
    )
    db.add(test_dept)
    
    # 创建开发部门
    dev_dept = Department(
        name="开发部",
        description="负责系统开发和维护"
    )
    db.add(dev_dept)
    
    db.commit()
    return [test_dept, dev_dept]

def init_admin_user(db):
    """初始化超级管理员用户"""
    # 获取超级管理员角色
    admin_role = db.query(Role).filter(Role.name == "超级管理员").first()
    
    # 创建超级管理员用户
    admin_user = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("admin123"),
        is_active=True,
        is_superuser=True,
        roles=[admin_role]
    )
    
    db.add(admin_user)
    db.commit()
    return admin_user

def init_data():
    """初始化所有数据"""
    db = SessionLocal()
    try:
        # 初始化权限
        print("正在初始化权限...")
        init_permissions(db)
        
        # 初始化角色
        print("正在初始化角色...")
        init_roles(db)
        
        # 初始化部门
        print("正在初始化部门...")
        init_departments(db)
        
        # 初始化超级管理员
        print("正在初始化超级管理员...")
        init_admin_user(db)
        
        print("数据初始化完成！")
        print("超级管理员账号：admin")
        print("超级管理员密码：admin123")
        
    except Exception as e:
        print(f"初始化数据失败: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    init_data() 