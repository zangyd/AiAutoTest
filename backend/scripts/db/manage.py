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
            password=DB_PASSWORD,  # PyMySQL会自动处理密码中的特殊字符
            database=database,
            charset='utf8mb4'
        )
        return connection
    except Exception as e:
        print(f"连接错误: {str(e)}")
        raise

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