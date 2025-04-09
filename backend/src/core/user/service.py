from typing import Optional
from sqlalchemy.orm import Session
from .models import User

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(self, username: str, password: str, email: str) -> User:
        """创建新用户"""
        user = User(
            username=username,
            password=password,
            email=email
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user 