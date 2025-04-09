import os
import sys
from urllib.parse import quote_plus

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.auth.models import User
from src.core.auth.security import get_password_hash

# 数据库连接配置
DB_USER = "root"
DB_PASS = quote_plus("Autotest@2024")  # 对特殊字符进行编码
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "autotest"

# 创建数据库引擎
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def reset_admin_password():
    """重置admin用户密码"""
    db = SessionLocal()
    try:
        # 获取admin用户
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            print("未找到admin用户")
            return
        
        # 重置密码
        new_password = "Autotest@2024"
        admin.password_hash = get_password_hash(new_password)
        
        # 确保用户处于激活状态
        admin.is_active = True
        admin.is_superuser = True
        admin.login_attempts = 0
        admin.locked_until = None
        
        db.commit()
        print(f"已重置admin用户密码为: {new_password}")
        
    except Exception as e:
        print(f"重置密码失败: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_admin_password() 