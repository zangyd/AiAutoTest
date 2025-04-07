"""
认证测试工具函数
"""
from datetime import datetime
from typing import Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.jwt import create_access_token, create_refresh_token
from core.auth.security import get_password_hash
from models.user import User

async def create_test_user(db: AsyncSession) -> User:
    """
    创建测试用户
    
    Args:
        db: 数据库会话
        
    Returns:
        User: 测试用户对象
    """
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("password123"),
        is_active=True,
        is_superuser=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        password_changed_at=datetime.utcnow()
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
    
async def get_test_token(user: User) -> Dict[str, Any]:
    """
    获取测试用令牌
    
    Args:
        user: 用户对象
        
    Returns:
        Dict[str, Any]: 包含访问令牌和刷新令牌的字典
    """
    access_token = await create_access_token({"sub": str(user.id)})
    refresh_token = await create_refresh_token({"sub": str(user.id)})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    } 