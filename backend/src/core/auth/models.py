"""
认证相关的数据库模型
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table, BigInteger, Text, UniqueConstraint, Index
from sqlalchemy.sql import text, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from core.models import Base, mapper_registry

__all__ = ['User', 'Role', 'Permission', 'Department', 'LoginLog', 'OperationLog', 'user_roles', 'user_departments', 'role_permissions']

# 用户-角色关联表
user_roles = Table(
    'user_roles',
    mapper_registry.metadata,
    Column('id', BigInteger, primary_key=True, autoincrement=True),
    Column('user_id', BigInteger, nullable=False),
    Column('role_id', BigInteger, nullable=False),
    Column('created_at', DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP')),
    UniqueConstraint('user_id', 'role_id', name='uk_user_role'),
    Index('ix_user_roles_user_id', 'user_id'),
    Index('ix_user_roles_role_id', 'role_id'),
    extend_existing=True
)

# 用户-部门关联表
user_departments = Table(
    'user_departments',
    mapper_registry.metadata,
    Column('id', BigInteger, primary_key=True, autoincrement=True),
    Column('user_id', BigInteger, nullable=False),
    Column('department_id', BigInteger, nullable=False),
    Column('created_at', DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间'),
    UniqueConstraint('user_id', 'department_id', name='uk_user_department'),
    Index('ix_user_departments_user_id', 'user_id'),
    Index('ix_user_departments_department_id', 'department_id'),
    extend_existing=True
)

# 角色-权限关联表
role_permissions = Table(
    'role_permissions',
    mapper_registry.metadata,
    Column('id', BigInteger, primary_key=True, autoincrement=True),
    Column('role_id', BigInteger, nullable=False),
    Column('permission_id', BigInteger, nullable=False),
    Column('created_at', DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间'),
    UniqueConstraint('role_id', 'permission_id', name='uk_role_permission'),
    Index('ix_role_permissions_role_id', 'role_id'),
    Index('ix_role_permissions_permission_id', 'permission_id'),
    extend_existing=True
)

class Permission(Base):
    """权限表"""
    __tablename__ = 'permissions'
    __table_args__ = {'extend_existing': True}
    
    # 主键
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    
    # 必填字段
    code: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    resource: Mapped[str] = mapped_column(String(200), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # 可选字段
    description: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    
    # 带默认值的字段
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    # 关系
    roles: Mapped[List["Role"]] = relationship(
        'Role',
        secondary='role_permissions',
        primaryjoin="Permission.id==role_permissions.c.permission_id",
        secondaryjoin="Role.id==role_permissions.c.role_id",
        back_populates="permissions",
        lazy='joined'
    )

class Role(Base):
    """角色模型"""
    __tablename__ = 'roles'
    __table_args__ = {'extend_existing': True}
    
    # 主键
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    
    # 必填字段
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    
    # 可选字段
    description: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    created_by: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # 带默认值的字段
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    # 关系
    permissions: Mapped[List[Permission]] = relationship(
        'Permission',
        secondary='role_permissions',
        primaryjoin="Role.id==role_permissions.c.role_id",
        secondaryjoin="Permission.id==role_permissions.c.permission_id",
        back_populates="roles",
        lazy='joined'
    )
    users: Mapped[List["User"]] = relationship(
        'User',
        secondary='user_roles',
        primaryjoin="Role.id==user_roles.c.role_id",
        secondaryjoin="User.id==user_roles.c.user_id",
        back_populates="roles",
        lazy='joined'
    )

class Department(Base):
    """部门表"""
    __tablename__ = 'departments'
    __table_args__ = {'extend_existing': True}
    
    # 主键
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    
    # 必填字段
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    
    # 可选字段
    description: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    parent_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    created_by: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # 带默认值的字段
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    # 关系
    users: Mapped[List["User"]] = relationship(
        'User',
        secondary='user_departments',
        remote_side='user_departments.c.department_id',
        lazy='joined'
    )

class User(Base):
    """用户表"""
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    
    # 主键
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    
    # 必填字段
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    real_name: Mapped[str] = mapped_column(String(50), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(200), nullable=False)
    
    # 可选字段
    created_by: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # 带默认值的字段
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    # 关系
    roles: Mapped[List[Role]] = relationship(
        'Role',
        secondary='user_roles',
        back_populates='users',
        lazy='joined'
    )
    departments: Mapped[List[Department]] = relationship(
        'Department',
        secondary='user_departments',
        remote_side='user_departments.c.user_id',
        lazy='joined'
    )

class LoginLog(Base):
    """登录日志表"""
    __tablename__ = 'login_logs'
    __table_args__ = {'extend_existing': True}
    
    # 主键
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    
    # 必填字段
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    login_time: Mapped[datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # 可选字段
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    message: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

class OperationLog(Base):
    """操作日志表"""
    __tablename__ = 'operation_logs'
    __table_args__ = {'extend_existing': True}
    
    # 主键
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    
    # 必填字段
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    operation_time: Mapped[datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    module: Mapped[str] = mapped_column(String(50), nullable=False)
    operation: Mapped[str] = mapped_column(String(50), nullable=False)
    method: Mapped[str] = mapped_column(String(20), nullable=False)
    url: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # 可选字段
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    request_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    response_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    message: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

# ... 其他模型 ... 