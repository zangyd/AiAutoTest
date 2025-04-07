"""
用户相关的数据库模型
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table, BigInteger, text, Text
from sqlalchemy.orm import relationship
from core.database import Base
from core.auth.models import User, Role, Permission, user_role, role_permission, Department

# Department模型已经在core.auth.models中定义，无需重复定义 