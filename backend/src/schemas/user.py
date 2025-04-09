from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserResponse(BaseModel):
    """用户信息响应模型"""
    id: int
    username: str
    nickname: Optional[str] = None
    email: Optional[str] = None
    avatar: Optional[str] = None
    role: str
    status: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 