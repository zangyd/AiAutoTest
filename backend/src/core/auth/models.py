"""
认证模块数据库模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table, BigInteger
from sqlalchemy.sql import text
from sqlalchemy.orm import relationship
from core.database import Base

# 用户-角色关联表
user_role = Table(
    'user_roles',
    Base.metadata,
    Column('id', BigInteger, primary_key=True, autoincrement=True),
    Column('user_id', BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    Column('role_id', BigInteger, ForeignKey('roles.id', ondelete='CASCADE'), nullable=False),
    Column('start_time', DateTime, nullable=True),
    Column('end_time', DateTime, nullable=True),
    Column('created_at', DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP')),
    extend_existing=True
)

# 角色-权限关联表
role_permission = Table(
    'role_permissions',
    Base.metadata,
    Column('id', BigInteger, primary_key=True, autoincrement=True),
    Column('role_id', BigInteger, ForeignKey('roles.id', ondelete='CASCADE'), nullable=False),
    Column('permission_id', BigInteger, ForeignKey('permissions.id', ondelete='CASCADE'), nullable=False),
    Column('created_at', DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP')),
    extend_existing=True
)

class User(Base):
    """用户表"""
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    real_name = Column(String(50), nullable=False)
    position = Column(String(50), nullable=True)
    is_active = Column(Boolean, nullable=True, server_default=text('1'))
    is_superuser = Column(Boolean, nullable=True, server_default=text('0'))
    login_attempts = Column(Integer, nullable=True, server_default=text('0'))
    locked_until = Column(DateTime, nullable=True)
    password_changed_at = Column(DateTime, nullable=True)
    last_login_at = Column(DateTime, nullable=True)
    last_login_ip = Column(String(50), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    created_by = Column(String(50), nullable=True)
    updated_by = Column(String(50), nullable=True)
    
    # 关系
    roles = relationship('Role', secondary=user_role, back_populates='users')
    department_id = Column(BigInteger, ForeignKey('departments.id'))
    department = relationship('Department', back_populates='users')

class Role(Base):
    """角色表"""
    __tablename__ = 'roles'
    __table_args__ = {'extend_existing': True}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(200), nullable=True)
    is_system = Column(Boolean, nullable=True, server_default=text('0'))
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    created_by = Column(String(50), nullable=True)
    updated_by = Column(String(50), nullable=True)
    
    # 关系
    users = relationship('User', secondary=user_role, back_populates='roles')
    permissions = relationship('Permission', secondary=role_permission, back_populates='roles')

class Permission(Base):
    """权限表"""
    __tablename__ = 'permissions'
    __table_args__ = {'extend_existing': True}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    code = Column(String(100), unique=True, nullable=False)
    name = Column(String(50), nullable=False)
    description = Column(String(200), nullable=True)
    type = Column(String(50), nullable=False)
    resource = Column(String(200), nullable=False)
    action = Column(String(50), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    
    # 关系
    roles = relationship('Role', secondary=role_permission, back_populates='permissions')

class Department(Base):
    """部门表"""
    __tablename__ = 'departments'
    __table_args__ = {'extend_existing': True}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(200), nullable=True)
    parent_id = Column(BigInteger, ForeignKey('departments.id'), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    
    # 关系
    parent = relationship('Department', remote_side=[id], backref='children')
    users = relationship('User', back_populates='department')

# ... 其他模型 ... 