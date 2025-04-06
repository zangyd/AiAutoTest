"""
数据库管理脚本
"""
import os
import sys
import click
from pathlib import Path
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv
import pymysql

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent.parent
backend_root = project_root / 'backend'
sys.path.append(str(project_root))
sys.path.append(str(backend_root))

# 加载环境变量
env_file = project_root / '.env'
if env_file.exists():
    print(f"加载配置文件: {env_file}")
    with open(env_file) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value.strip()

load_dotenv()

# 数据库配置
DB_USER = os.getenv('MYSQL_USER', 'root')
DB_PASSWORD = os.getenv('MYSQL_PASSWORD', 'Autotest@2024')
DB_HOST = os.getenv('MYSQL_HOST', 'localhost')
DB_PORT = int(os.getenv('MYSQL_PORT', 3306))
DB_NAME = os.getenv('MYSQL_DATABASE', 'autotest')

def get_connection(database=None):
    """获取数据库连接"""
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,  # 直接使用原始密码
            database=database,
            charset='utf8mb4'
        )
        return connection
    except Exception as e:
        print(f"连接错误: {str(e)}")
        raise

def database_exists():
    """检查数据库是否存在"""
    try:
        # 连接到MySQL服务器（不指定数据库）
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{DB_NAME}'")
            result = cursor.fetchone()
            return result is not None
    except Exception as e:
        print(f"检查数据库存在时出错: {str(e)}")
        return False
    finally:
        if 'connection' in locals():
            connection.close()

def create_database():
    """创建数据库"""
    try:
        # 连接到MySQL服务器（不指定数据库）
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        connection.commit()
        print(f"数据库 {DB_NAME} 创建成功")
    except Exception as e:
        print(f"创建数据库时出错: {str(e)}")
        raise
    finally:
        if 'connection' in locals():
            connection.close()

def get_engine(database_name=None):
    """获取SQLAlchemy引擎"""
    try:
        # 打印连接信息
        print(f"数据库连接信息:")
        print(f"用户: {DB_USER}")
        print(f"主机: {DB_HOST}")
        print(f"端口: {DB_PORT}")
        print(f"数据库: {database_name or DB_NAME}")
        
        # 使用pymysql创建连接
        connection = get_connection(database_name or DB_NAME)
        connection.close()
        
        # 创建SQLAlchemy引擎，对密码进行URL编码
        engine = create_engine(
            f"mysql+pymysql://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{database_name or DB_NAME}",
            pool_pre_ping=True
        )
        return engine
    except Exception as e:
        print(f"创建数据库引擎时出错: {str(e)}")
        raise

@click.group()
def cli():
    """数据库管理工具"""
    pass

@cli.command()
def init():
    """初始化数据库"""
    print("正在初始化数据库...")
    
    if not database_exists():
        print(f"数据库 {DB_NAME} 不存在，正在创建...")
        create_database()
    else:
        print(f"数据库 {DB_NAME} 已存在")
    
    # 验证连接
    engine = get_engine()
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print("数据库连接测试成功")
    except Exception as e:
        print(f"数据库连接测试失败: {str(e)}")
        raise

@cli.command()
def migrate():
    """执行数据库迁移"""
    try:
        # 切换到migrations目录执行迁移
        migrations_dir = backend_root / 'src' / 'migrations'
        os.chdir(str(migrations_dir))
        os.system('alembic upgrade head')
        print("数据库迁移完成")
    except Exception as e:
        print(f"迁移失败: {e}")
        sys.exit(1)

@cli.command()
def rollback():
    """回滚上一次迁移"""
    try:
        # 切换到migrations目录执行回滚
        migrations_dir = backend_root / 'src' / 'migrations'
        os.chdir(str(migrations_dir))
        os.system('alembic downgrade -1')
        print("数据库回滚完成")
    except Exception as e:
        print(f"回滚失败: {e}")
        sys.exit(1)

@cli.command()
@click.argument('message')
def create(message):
    """创建新的迁移版本"""
    try:
        # 切换到migrations目录创建迁移
        migrations_dir = backend_root / 'src' / 'migrations'
        os.chdir(str(migrations_dir))
        os.system(f'alembic revision --autogenerate -m "{message}"')
        print("迁移文件创建完成")
    except Exception as e:
        print(f"创建迁移文件失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    cli() 