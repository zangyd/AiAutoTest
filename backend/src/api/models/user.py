"""
用户相关模型
"""
from core.auth.models import User, Department

__all__ = ['User', 'Department']

# Department模型已经在core.auth.models中定义，无需重复定义 