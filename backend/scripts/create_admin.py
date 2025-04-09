"""
创建管理员用户的脚本
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from core.auth.models import User, Role, Permission, role_permissions, user_roles
from core.auth.security import get_password_hash
from core.config import settings

def create_admin_user():
    """创建管理员用户及相关角色权限"""
    # 创建数据库连接
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
    
    try:
        with Session(engine) as session:
            # 检查管理员用户是否已存在
            admin = session.query(User).filter(User.username == 'admin').first()
            if admin:
                print("管理员用户已存在")
                return
            
            # 创建基础权限
            permissions = []
            for code, name in [
                ('user:manage', '用户管理'),
                ('role:manage', '角色管理'),
                ('permission:manage', '权限管理'),
                ('department:manage', '部门管理'),
                ('system:manage', '系统管理')
            ]:
                permission = Permission(
                    code=code,
                    name=name,
                    type='system',
                    resource=f'/api/v1/{code.split(":")[0]}',
                    action=code.split(':')[1]
                )
                session.add(permission)
                permissions.append(permission)
            
            # 创建超级管理员角色
            admin_role = Role(
                name='超级管理员',
                description='系统超级管理员，拥有所有权限',
                is_system=True
            )
            session.add(admin_role)
            
            # 为角色分配所有权限
            for permission in permissions:
                session.execute(
                    role_permissions.insert().values(
                        role_id=admin_role.id,
                        permission_id=permission.id
                    )
                )
            
            # 创建管理员用户
            admin_user = User(
                username='admin',
                email='admin@example.com',
                real_name='系统管理员',
                password_hash=get_password_hash('admin123'),
                is_active=True,
                is_superuser=True
            )
            session.add(admin_user)
            
            # 为用户分配超级管理员角色
            session.execute(
                user_roles.insert().values(
                    user_id=admin_user.id,
                    role_id=admin_role.id
                )
            )
            
            session.commit()
            print("管理员用户创建成功")
            
    except Exception as e:
        print(f"创建管理员用户失败: {str(e)}")
        session.rollback()
        raise

if __name__ == '__main__':
    create_admin_user() 