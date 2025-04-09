"""
初始化数据脚本
"""
import os
import sys
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from core.database.session import SessionLocal, Base, engine
from core.auth.models import User, Role, Permission, Department
from core.security import get_password_hash
from core.config.settings import settings

def init_database():
    """初始化数据库表"""
    Base.metadata.create_all(bind=engine)

def init_permissions(db):
    """初始化权限"""
    permissions = [
        {
            "name": "用户管理",
            "code": "user:manage",
            "description": "用户的增删改查权限",
            "type": "system",
            "resource": "user",
            "action": "manage"
        },
        {
            "name": "角色管理",
            "code": "role:manage",
            "description": "角色的增删改查权限",
            "type": "system",
            "resource": "role",
            "action": "manage"
        },
        {
            "name": "部门管理",
            "code": "department:manage",
            "description": "部门的增删改查权限",
            "type": "system",
            "resource": "department",
            "action": "manage"
        }
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
        description="系统超级管理员",
        is_system=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        created_by="system",
        updated_by="system"
    )
    db.add(admin_role)
    db.flush()  # 刷新以获取role_id
    
    # 为超级管理员添加所有权限
    for permission in all_permissions:
        admin_role.permissions.append(permission)
    
    # 创建部门管理员角色
    dept_permissions = db.query(Permission).filter(
        Permission.code.in_([
            "department:manage",
            "user:manage"
        ])
    ).all()
    
    dept_role = Role(
        name="部门管理员",
        description="部门管理员",
        is_system=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        created_by="system",
        updated_by="system"
    )
    db.add(dept_role)
    db.flush()  # 刷新以获取role_id
    
    # 为部门管理员添加指定权限
    for permission in dept_permissions:
        dept_role.permissions.append(permission)
    
    db.commit()
    return [admin_role, dept_role]

def init_users(db):
    """初始化用户"""
    # 获取超级管理员角色
    admin_role = db.query(Role).filter(Role.name == "超级管理员").first()
    dept_role = db.query(Role).filter(Role.name == "部门管理员").first()
    
    # 从环境变量获取密码，如果没有则使用默认密码
    admin_password = os.getenv('ADMIN_PASSWORD', settings.MYSQL_PASSWORD)
    
    # 创建超级管理员用户
    admin_user = User(
        username="admin",
        email="admin@example.com",
        password_hash=get_password_hash(admin_password),
        real_name="系统管理员",
        position="系统管理员",
        is_active=True,
        is_superuser=True,
        login_attempts=0,
        locked_until=None,
        password_changed_at=datetime.utcnow(),
        last_login_at=None,
        last_login_ip=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        created_by="system",
        updated_by="system",
        roles=[admin_role]
    )
    
    # 创建测试管理员用户
    test_admin = User(
        username="test_admin",
        email="test@example.com",
        password_hash=get_password_hash(admin_password),
        real_name="测试管理员",
        position="测试管理员",
        is_active=True,
        is_superuser=False,
        login_attempts=0,
        locked_until=None,
        password_changed_at=datetime.utcnow(),
        last_login_at=None,
        last_login_ip=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        created_by="system",
        updated_by="system",
        roles=[dept_role]
    )
    
    db.add(admin_user)
    db.add(test_admin)
    db.commit()
    return [admin_user, test_admin]

def init_data():
    """初始化所有数据"""
    # 初始化数据库表
    print("正在初始化数据库表...")
    init_database()
    
    db = SessionLocal()
    try:
        # 初始化权限
        print("正在初始化权限...")
        init_permissions(db)
        
        # 初始化角色
        print("正在初始化角色...")
        init_roles(db)
        
        # 初始化用户
        print("正在初始化用户...")
        init_users(db)
        
        print("数据初始化完成！")
        print(f"超级管理员账号：admin")
        print(f"超级管理员密码：{os.getenv('ADMIN_PASSWORD', settings.MYSQL_PASSWORD)}")
        print(f"测试管理员账号：test_admin")
        print(f"测试管理员密码：{os.getenv('ADMIN_PASSWORD', settings.MYSQL_PASSWORD)}")
        
    except Exception as e:
        print(f"初始化数据失败: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == '__main__':
    init_data() 