"""添加初始用户数据

Revision ID: 003
Revises: 002
Create Date: 2024-04-06 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime
import bcrypt

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 获取连接
    connection = op.get_bind()

    # 创建用户表数据
    users_table = sa.table('users',
        sa.column('id', sa.BigInteger),
        sa.column('username', sa.String),
        sa.column('email', sa.String),
        sa.column('password_hash', sa.String),
        sa.column('real_name', sa.String),
        sa.column('position', sa.String),
        sa.column('is_active', sa.Boolean),
        sa.column('is_superuser', sa.Boolean),
        sa.column('login_attempts', sa.Integer),
        sa.column('locked_until', sa.TIMESTAMP),
        sa.column('password_changed_at', sa.TIMESTAMP),
        sa.column('last_login_at', sa.TIMESTAMP),
        sa.column('last_login_ip', sa.String),
        sa.column('created_at', sa.TIMESTAMP),
        sa.column('updated_at', sa.TIMESTAMP),
        sa.column('created_by', sa.String),
        sa.column('updated_by', sa.String)
    )

    # 生成加密密码
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode()

    # 插入超级管理员用户
    current_time = datetime.now()
    op.bulk_insert(users_table, [
        {
            'username': 'admin',
            'email': 'admin@example.com',
            'password_hash': hash_password('Admin@2024'),
            'real_name': '系统管理员',
            'position': '系统管理员',
            'is_active': True,
            'is_superuser': True,
            'login_attempts': 0,
            'locked_until': None,
            'password_changed_at': current_time,
            'last_login_at': None,
            'last_login_ip': None,
            'created_at': current_time,
            'updated_at': current_time,
            'created_by': 'system',
            'updated_by': 'system'
        },
        {
            'username': 'test_admin',
            'email': 'test@example.com',
            'password_hash': hash_password('Test@2024'),
            'real_name': '测试管理员',
            'position': '测试管理员',
            'is_active': True,
            'is_superuser': False,
            'login_attempts': 0,
            'locked_until': None,
            'password_changed_at': current_time,
            'last_login_at': None,
            'last_login_ip': None,
            'created_at': current_time,
            'updated_at': current_time,
            'created_by': 'system',
            'updated_by': 'system'
        }
    ])

    # 创建用户-角色关联
    user_roles_table = sa.table('user_roles',
        sa.column('id', sa.BigInteger),
        sa.column('user_id', sa.BigInteger),
        sa.column('role_id', sa.BigInteger),
        sa.column('start_time', sa.TIMESTAMP),
        sa.column('end_time', sa.TIMESTAMP),
        sa.column('created_at', sa.TIMESTAMP)
    )

    # 获取插入的用户ID
    result = connection.execute(sa.text("SELECT id FROM users WHERE username IN ('admin', 'test_admin')"))
    user_ids = {row[0] for row in result}
    admin_id = min(user_ids)  # admin用户应该是第一个创建的
    test_admin_id = max(user_ids)  # test_admin是第二个创建的

    # admin用户分配超级管理员角色
    op.bulk_insert(user_roles_table, [
        {
            'user_id': admin_id,
            'role_id': 1,  # 超级管理员角色
            'start_time': current_time,
            'end_time': None,
            'created_at': current_time
        },
        {
            'user_id': test_admin_id,
            'role_id': 2,  # 部门管理员角色
            'start_time': current_time,
            'end_time': None,
            'created_at': current_time
        }
    ])

    # 创建用户-部门关联
    user_departments_table = sa.table('user_departments',
        sa.column('id', sa.BigInteger),
        sa.column('user_id', sa.BigInteger),
        sa.column('department_id', sa.BigInteger),
        sa.column('is_leader', sa.Boolean),
        sa.column('created_at', sa.TIMESTAMP)
    )

    # 将用户关联到部门
    op.bulk_insert(user_departments_table, [
        {
            'user_id': admin_id,
            'department_id': 1,  # 总部
            'is_leader': True,  # admin是总部的负责人
            'created_at': current_time
        },
        {
            'user_id': test_admin_id,
            'department_id': 3,  # 测试部
            'is_leader': True,  # test_admin是测试部的负责人
            'created_at': current_time
        }
    ])

def downgrade() -> None:
    # 删除数据（注意顺序，先删除有外键约束的数据）
    connection = op.get_bind()
    
    # 获取用户ID
    result = connection.execute(sa.text("SELECT id FROM users WHERE username IN ('admin', 'test_admin')"))
    user_ids = [str(row[0]) for row in result]
    if user_ids:
        id_list = ','.join(user_ids)
        connection.execute(sa.text(f'DELETE FROM user_departments WHERE user_id IN ({id_list})'))
        connection.execute(sa.text(f'DELETE FROM user_roles WHERE user_id IN ({id_list})'))
        connection.execute(sa.text(f'DELETE FROM users WHERE id IN ({id_list})')) 