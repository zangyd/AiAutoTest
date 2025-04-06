"""初始迁移

Revision ID: 001
Revises: 
Create Date: 2024-04-06 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 创建departments表
    op.create_table(
        'departments',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('description', sa.String(200), nullable=True),
        sa.Column('parent_id', sa.BigInteger, nullable=True),
        sa.Column('level', sa.Integer, nullable=False),
        sa.Column('path', sa.String(500), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.Column('created_by', sa.String(50), nullable=True),
        sa.Column('updated_by', sa.String(50), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['departments.id']),
        sa.UniqueConstraint('name')
    )

    # 创建permissions表
    op.create_table(
        'permissions',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('code', sa.String(100), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('description', sa.String(200), nullable=True),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('resource', sa.String(200), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.UniqueConstraint('code')
    )

    # 创建roles表
    op.create_table(
        'roles',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('description', sa.String(200), nullable=True),
        sa.Column('is_system', sa.Boolean, nullable=True, server_default=sa.text('0')),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.Column('created_by', sa.String(50), nullable=True),
        sa.Column('updated_by', sa.String(50), nullable=True),
        sa.UniqueConstraint('name')
    )

    # 创建role_permissions表
    op.create_table(
        'role_permissions',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('role_id', sa.BigInteger, nullable=False),
        sa.Column('permission_id', sa.BigInteger, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id']),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id']),
        sa.UniqueConstraint('role_id', 'permission_id')
    )

    # 创建users表
    op.create_table(
        'users',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('email', sa.String(100), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('real_name', sa.String(50), nullable=False),
        sa.Column('position', sa.String(50), nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=True, server_default=sa.text('1')),
        sa.Column('is_superuser', sa.Boolean, nullable=True, server_default=sa.text('0')),
        sa.Column('login_attempts', sa.Integer, nullable=True, server_default=sa.text('0')),
        sa.Column('locked_until', sa.TIMESTAMP, nullable=True),
        sa.Column('password_changed_at', sa.TIMESTAMP, nullable=True),
        sa.Column('last_login_at', sa.TIMESTAMP, nullable=True),
        sa.Column('last_login_ip', sa.String(50), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.Column('created_by', sa.String(50), nullable=True),
        sa.Column('updated_by', sa.String(50), nullable=True),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )

    # 创建user_roles表
    op.create_table(
        'user_roles',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.BigInteger, nullable=False),
        sa.Column('role_id', sa.BigInteger, nullable=False),
        sa.Column('start_time', sa.TIMESTAMP, nullable=True),
        sa.Column('end_time', sa.TIMESTAMP, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id']),
        sa.UniqueConstraint('user_id', 'role_id')
    )

    # 创建user_departments表
    op.create_table(
        'user_departments',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.BigInteger, nullable=False),
        sa.Column('department_id', sa.BigInteger, nullable=False),
        sa.Column('is_leader', sa.Boolean, nullable=True, server_default=sa.text('0')),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id']),
        sa.UniqueConstraint('user_id', 'department_id')
    )

    # 创建operation_logs表
    op.create_table(
        'operation_logs',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.BigInteger, nullable=False),
        sa.Column('operation_type', sa.String(50), nullable=False),
        sa.Column('operation_content', sa.String(200), nullable=False),
        sa.Column('ip_address', sa.String(50), nullable=True),
        sa.Column('user_agent', sa.String(200), nullable=True),
        sa.Column('status', sa.Integer, nullable=False, server_default=sa.text('1')),
        sa.Column('error_message', sa.String(500), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.Index('idx_operation_type', 'operation_type'),
        sa.Index('idx_created_at', 'created_at')
    )

def downgrade() -> None:
    # 按照相反的顺序删除表（考虑外键约束）
    op.drop_table('operation_logs')
    op.drop_table('user_departments')
    op.drop_table('user_roles')
    op.drop_table('users')
    op.drop_table('role_permissions')
    op.drop_table('roles')
    op.drop_table('permissions')
    op.drop_table('departments') 