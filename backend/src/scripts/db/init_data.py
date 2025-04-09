"""
初始化数据脚本
"""
import os
import sys
from datetime import datetime
from sqlalchemy import inspect

# 添加项目根目录到 Python 路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from core.database.session import SessionLocal, Base, engine
from core.auth.models import User, Role, Permission, Department, role_permissions, user_roles
from core.security import get_password_hash
from core.config.settings import settings
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_tables_exist():
    """验证必要的表是否存在"""
    try:
        with engine.connect() as conn:
            # 检查每个表是否存在
            tables = ['permissions', 'roles', 'users', 'role_permissions', 'user_roles']
            inspector = inspect(engine)
            existing_tables = inspector.get_table_names()
            
            for table in tables:
                if table not in existing_tables:
                    logger.error(f"表 {table} 不存在")
                    return False
                else:
                    logger.info(f"表 {table} 已存在")
        return True
    except Exception as e:
        logger.error(f"验证表存在时发生错误: {str(e)}")
        return False

def init_database():
    """初始化数据库表"""
    logger.info("开始创建数据库表...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建完成")
        
        # 验证表是否创建成功
        if not verify_tables_exist():
            raise Exception("数据库表创建失败，请检查数据库连接和权限")
            
    except Exception as e:
        logger.error(f"创建数据库表时发生错误: {str(e)}")
        raise

def clean_tables(db):
    """清空相关表的数据"""
    logger.info("开始清空表数据...")
    try:
        # 按照外键依赖关系，从下往上清空
        db.execute(user_roles.delete())
        db.execute(role_permissions.delete())
        db.query(User).delete()
        db.query(Role).delete()
        db.query(Permission).delete()
        db.commit()
        logger.info("表数据清空完成")
    except Exception as e:
        db.rollback()
        logger.error(f"清空表数据时发生错误: {str(e)}")
        raise

def init_permissions(db):
    """初始化权限"""
    logger.info("开始初始化权限数据...")
    now = datetime.utcnow()
    permissions = [
        {
            "name": "用户管理",
            "code": "user:manage",
            "description": "用户的增删改查权限",
            "type": "system",
            "resource": "user",
            "action": "manage",
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "角色管理",
            "code": "role:manage",
            "description": "角色的增删改查权限",
            "type": "system",
            "resource": "role",
            "action": "manage",
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "部门管理",
            "code": "department:manage",
            "description": "部门的增删改查权限",
            "type": "system",
            "resource": "department",
            "action": "manage",
            "created_at": now,
            "updated_at": now
        }
    ]
    
    try:
        for perm_data in permissions:
            logger.info(f"添加权限: {perm_data['name']}")
            perm = Permission(**perm_data)
            db.add(perm)
        
        db.commit()
        logger.info("权限数据初始化完成")
    except Exception as e:
        db.rollback()
        logger.error(f"初始化权限数据时发生错误: {str(e)}")
        raise
    return permissions

def init_roles(db):
    """初始化角色"""
    logger.info("开始初始化角色数据...")
    try:
        # 获取所有权限
        all_permissions = db.query(Permission).all()
        logger.info(f"找到 {len(all_permissions)} 个权限")
        now = datetime.utcnow()
        
        # 创建超级管理员角色
        admin_role = Role(
            name="超级管理员",
            description="系统超级管理员",
            is_system=False,
            created_at=now,
            updated_at=now
        )
        db.add(admin_role)
        db.flush()  # 刷新以获取role_id
        logger.info(f"创建超级管理员角色，ID: {admin_role.id}")
        
        # 为超级管理员添加所有权限
        for permission in all_permissions:
            db.execute(
                role_permissions.insert().values(
                    role_id=admin_role.id,
                    permission_id=permission.id,
                    created_at=now
                )
            )
            logger.info(f"为超级管理员添加权限: {permission.name}")
        
        # 创建部门管理员角色
        dept_permissions = db.query(Permission).filter(
            Permission.code.in_([
                "department:manage",
                "user:manage"
            ])
        ).all()
        logger.info(f"找到 {len(dept_permissions)} 个部门管理员权限")
        
        dept_role = Role(
            name="部门管理员",
            description="部门管理员",
            is_system=False,
            created_at=now,
            updated_at=now
        )
        db.add(dept_role)
        db.flush()  # 刷新以获取role_id
        logger.info(f"创建部门管理员角色，ID: {dept_role.id}")
        
        # 为部门管理员添加指定权限
        for permission in dept_permissions:
            db.execute(
                role_permissions.insert().values(
                    role_id=dept_role.id,
                    permission_id=permission.id,
                    created_at=now
                )
            )
            logger.info(f"为部门管理员添加权限: {permission.name}")
        
        db.commit()
        logger.info("角色数据初始化完成")
    except Exception as e:
        db.rollback()
        logger.error(f"初始化角色数据时发生错误: {str(e)}")
        raise
    return [admin_role, dept_role]

def init_users(db):
    """初始化用户"""
    logger.info("开始初始化用户数据...")
    try:
        # 获取超级管理员角色
        admin_role = db.query(Role).filter(Role.name == "超级管理员").first()
        dept_role = db.query(Role).filter(Role.name == "部门管理员").first()
        
        if not admin_role or not dept_role:
            raise Exception("未找到必要的角色")
            
        logger.info(f"找到超级管理员角色，ID: {admin_role.id}")
        logger.info(f"找到部门管理员角色，ID: {dept_role.id}")
        
        now = datetime.utcnow()
        
        # 从环境变量获取密码，如果没有则使用默认密码
        admin_password = os.getenv('ADMIN_PASSWORD', settings.MYSQL_PASSWORD)
        
        # 创建超级管理员用户
        admin_user = User(
            username="admin",
            email="admin@example.com",
            password_hash=get_password_hash(admin_password),
            real_name="系统管理员",
            is_active=True,
            is_superuser=True,
            login_attempts=0,
            locked_until=None,
            created_at=now,
            updated_at=now
        )
        db.add(admin_user)
        db.flush()  # 刷新以获取user_id
        logger.info(f"创建超级管理员用户，ID: {admin_user.id}")
        
        # 为超级管理员添加角色
        db.execute(
            user_roles.insert().values(
                user_id=admin_user.id,
                role_id=admin_role.id,
                created_at=now
            )
        )
        logger.info("为超级管理员用户添加超级管理员角色")
        
        # 创建测试管理员用户
        test_admin = User(
            username="test_admin",
            email="test@example.com",
            password_hash=get_password_hash(admin_password),
            real_name="测试管理员",
            is_active=True,
            is_superuser=False,
            login_attempts=0,
            locked_until=None,
            created_at=now,
            updated_at=now
        )
        db.add(test_admin)
        db.flush()  # 刷新以获取user_id
        logger.info(f"创建测试管理员用户，ID: {test_admin.id}")
        
        # 为测试管理员添加角色
        db.execute(
            user_roles.insert().values(
                user_id=test_admin.id,
                role_id=dept_role.id,
                created_at=now
            )
        )
        logger.info("为测试管理员用户添加部门管理员角色")
        
        db.commit()
        logger.info("用户数据初始化完成")
    except Exception as e:
        db.rollback()
        logger.error(f"初始化用户数据时发生错误: {str(e)}")
        raise

def main():
    """主函数"""
    logger.info("开始数据初始化...")
    try:
        # 初始化数据库表
        init_database()
        
        # 创建数据库会话
        db = SessionLocal()
        try:
            # 清空表数据
            clean_tables(db)
            
            # 初始化权限
            init_permissions(db)
            
            # 初始化角色
            init_roles(db)
            
            # 初始化用户
            init_users(db)
            
            logger.info("数据初始化完成")
        except Exception as e:
            logger.error(f"数据初始化过程中发生错误: {str(e)}")
            raise
        finally:
            db.close()
    except Exception as e:
        logger.error(f"数据初始化失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()