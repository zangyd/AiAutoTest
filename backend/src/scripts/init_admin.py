"""初始化admin用户"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.config import settings
from src.core.auth.models import User, Base
from src.core.security import get_password_hash

def init_admin():
    """初始化admin用户"""
    # 创建数据库引擎和会话
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # 确保表存在
    Base.metadata.create_all(bind=engine)
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        # 检查admin用户是否存在
        user = db.query(User).filter(User.username == 'admin').first()
        if user:
            print('Admin user already exists')
            return
        
        # 创建admin用户
        admin = User(
            username='admin',
            password_hash=get_password_hash('Admin@2024'),
            email='admin@example.com',
            is_active=True,
            is_superuser=True
        )
        
        db.add(admin)
        db.commit()
        print('Successfully created admin user')
        
    except Exception as e:
        db.rollback()
        print(f'Failed to create admin user: {str(e)}')
        
    finally:
        db.close()

if __name__ == '__main__':
    init_admin() 