import os
import sys
from urllib.parse import quote_plus

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.core.auth.models import Base

# 数据库连接配置
DB_USER = "root"
DB_PASS = quote_plus("Autotest@2024")  # 对特殊字符进行编码
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "autotest"

# 创建数据库引擎
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

def recreate_tables():
    """重新创建数据库表"""
    try:
        # 删除现有的表
        Base.metadata.drop_all(bind=engine)
        print("已删除现有表")
        
        # 创建新表
        Base.metadata.create_all(bind=engine)
        print("已创建新表")
        
    except Exception as e:
        print(f"重新创建表失败: {str(e)}")

if __name__ == "__main__":
    recreate_tables() 