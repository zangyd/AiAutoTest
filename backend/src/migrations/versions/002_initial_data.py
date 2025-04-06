"""添加初始数据

Revision ID: 002
Revises: 001
Create Date: 2024-04-06 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 获取连接
    connection = op.get_bind()

    # 插入部门数据
    departments_table = sa.table('departments',
        sa.column('id', sa.BigInteger),
        sa.column('name', sa.String),
        sa.column('description', sa.String),
        sa.column('parent_id', sa.BigInteger),
        sa.column('level', sa.Integer),
        sa.column('path', sa.String),
        sa.column('created_at', sa.TIMESTAMP),
        sa.column('updated_at', sa.TIMESTAMP),
        sa.column('created_by', sa.String),
        sa.column('updated_by', sa.String)
    )

    # 插入根部门
    op.bulk_insert(departments_table, [
        {
            'id': 1,
            'name': '总部',
            'description': '公司总部',
            'parent_id': None,
            'level': 1,
            'path': '/1',
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'created_by': 'system',
            'updated_by': 'system'
        }
    ])

    # 插入二级部门
    op.bulk_insert(departments_table, [
        {
            'id': 2,
            'name': '研发部',
            'description': '负责产品研发',
            'parent_id': 1,
            'level': 2,
            'path': '/1/2',
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'created_by': 'system',
            'updated_by': 'system'
        },
        {
            'id': 3,
            'name': '测试部',
            'description': '负责产品测试',
            'parent_id': 1,
            'level': 2,
            'path': '/1/3',
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'created_by': 'system',
            'updated_by': 'system'
        }
    ])

    # 插入权限数据
    permissions_table = sa.table('permissions',
        sa.column('id', sa.BigInteger),
        sa.column('code', sa.String),
        sa.column('name', sa.String),
        sa.column('description', sa.String),
        sa.column('type', sa.String),
        sa.column('resource', sa.String),
        sa.column('action', sa.String),
        sa.column('created_at', sa.TIMESTAMP),
        sa.column('updated_at', sa.TIMESTAMP)
    )

    op.bulk_insert(permissions_table, [
        {
            'id': 1,
            'code': 'user:manage',
            'name': '用户管理',
            'description': '用户的增删改查权限',
            'type': 'system',
            'resource': 'user',
            'action': 'manage',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        },
        {
            'id': 2,
            'code': 'role:manage',
            'name': '角色管理',
            'description': '角色的增删改查权限',
            'type': 'system',
            'resource': 'role',
            'action': 'manage',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        },
        {
            'id': 3,
            'code': 'department:manage',
            'name': '部门管理',
            'description': '部门的增删改查权限',
            'type': 'system',
            'resource': 'department',
            'action': 'manage',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
    ])

    # 插入角色数据
    roles_table = sa.table('roles',
        sa.column('id', sa.BigInteger),
        sa.column('name', sa.String),
        sa.column('description', sa.String),
        sa.column('is_system', sa.Boolean),
        sa.column('created_at', sa.TIMESTAMP),
        sa.column('updated_at', sa.TIMESTAMP),
        sa.column('created_by', sa.String),
        sa.column('updated_by', sa.String)
    )

    op.bulk_insert(roles_table, [
        {
            'id': 1,
            'name': '超级管理员',
            'description': '系统超级管理员',
            'is_system': True,
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'created_by': 'system',
            'updated_by': 'system'
        },
        {
            'id': 2,
            'name': '部门管理员',
            'description': '部门管理员',
            'is_system': True,
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'created_by': 'system',
            'updated_by': 'system'
        }
    ])

    # 插入角色-权限关联数据
    role_permissions_table = sa.table('role_permissions',
        sa.column('id', sa.BigInteger),
        sa.column('role_id', sa.BigInteger),
        sa.column('permission_id', sa.BigInteger),
        sa.column('created_at', sa.TIMESTAMP)
    )

    # 超级管理员拥有所有权限
    op.bulk_insert(role_permissions_table, [
        {'role_id': 1, 'permission_id': 1, 'created_at': datetime.now()},
        {'role_id': 1, 'permission_id': 2, 'created_at': datetime.now()},
        {'role_id': 1, 'permission_id': 3, 'created_at': datetime.now()}
    ])

    # 部门管理员拥有部门管理权限
    op.bulk_insert(role_permissions_table, [
        {'role_id': 2, 'permission_id': 3, 'created_at': datetime.now()}
    ])

def downgrade() -> None:
    # 删除数据（注意顺序，先删除有外键约束的数据）
    connection = op.get_bind()
    connection.execute(sa.text('DELETE FROM role_permissions'))
    connection.execute(sa.text('DELETE FROM roles'))
    connection.execute(sa.text('DELETE FROM permissions'))
    connection.execute(sa.text('DELETE FROM departments')) 