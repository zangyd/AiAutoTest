"""
用户相关的数据库操作服务
"""
from typing import List, Optional, Set
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from api.models.user import Department
from core.auth.models import User, Role, Permission
from core.security import get_password_hash, verify_password

class UserService:
    """用户服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return self.db.query(User).filter(User.email == email).first()
    
    def create_user(self, username: str, email: str, password: str, 
                   department_id: Optional[int] = None,
                   role_ids: Optional[List[int]] = None) -> User:
        """创建用户"""
        # 检查用户名和邮箱是否已存在
        if self.get_user_by_username(username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        if self.get_user_by_email(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在"
            )
        
        # 创建用户
        user = User(
            username=username,
            email=email,
            password_hash=get_password_hash(password),
            department_id=department_id
        )
        
        # 添加角色
        if role_ids:
            roles = self.db.query(Role).filter(Role.id.in_(role_ids)).all()
            user.roles = roles
        
        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="创建用户失败"
            )
    
    def update_user(self, user_id: int, **kwargs) -> User:
        """更新用户信息"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 更新密码
        if "password" in kwargs:
            kwargs["password_hash"] = get_password_hash(kwargs.pop("password"))
        
        # 更新角色
        if "role_ids" in kwargs:
            roles = self.db.query(Role).filter(Role.id.in_(kwargs.pop("role_ids"))).all()
            user.roles = roles
        
        # 更新其他字段
        for key, value in kwargs.items():
            setattr(user, key, value)
        
        try:
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="更新用户失败"
            )
    
    def delete_user(self, user_id: int) -> bool:
        """删除用户"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        try:
            self.db.delete(user)
            self.db.commit()
            return True
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="删除用户失败"
            )
    
    def verify_password(self, user: User, password: str) -> bool:
        """验证用户密码"""
        return verify_password(password, user.password_hash)
    
    def get_user_permissions(self, user: User) -> Set[str]:
        """获取用户权限"""
        permissions = set()
        for role in user.roles:
            for permission in role.permissions:
                permissions.add(permission.code)
        return permissions

class RoleService:
    """角色服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_role_by_id(self, role_id: int) -> Optional[Role]:
        """根据ID获取角色"""
        return self.db.query(Role).filter(Role.id == role_id).first()
    
    def get_role_by_name(self, name: str) -> Optional[Role]:
        """根据名称获取角色"""
        return self.db.query(Role).filter(Role.name == name).first()
    
    def create_role(self, name: str, description: Optional[str] = None,
                   permission_ids: Optional[List[int]] = None) -> Role:
        """创建角色"""
        if self.get_role_by_name(name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="角色名已存在"
            )
        
        role = Role(name=name, description=description)
        
        if permission_ids:
            permissions = self.db.query(Permission).filter(Permission.id.in_(permission_ids)).all()
            role.permissions = permissions
        
        try:
            self.db.add(role)
            self.db.commit()
            self.db.refresh(role)
            return role
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="创建角色失败"
            )

class DepartmentService:
    """部门服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_department_by_id(self, department_id: int) -> Optional[Department]:
        """根据ID获取部门"""
        return self.db.query(Department).filter(Department.id == department_id).first()
    
    def get_department_by_name(self, name: str) -> Optional[Department]:
        """根据名称获取部门"""
        return self.db.query(Department).filter(Department.name == name).first()
    
    def create_department(self, name: str, parent_id: Optional[int] = None,
                        description: Optional[str] = None) -> Department:
        """创建部门"""
        if self.get_department_by_name(name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="部门名已存在"
            )
        
        department = Department(
            name=name,
            parent_id=parent_id,
            description=description
        )
        
        try:
            self.db.add(department)
            self.db.commit()
            self.db.refresh(department)
            return department
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="创建部门失败"
            ) 