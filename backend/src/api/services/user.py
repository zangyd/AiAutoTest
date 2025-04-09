"""
用户相关的数据库操作服务
"""
from typing import List, Optional, Set, Dict
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
import logging

from core.auth.models import User, Role, Permission, Department, user_roles, role_permissions
from core.security import get_password_hash, verify_password
from core.database import session
from core.logging.logger import Logger

# 创建用户服务日志记录器
user_logger = Logger(
    name="user_service",
    log_dir="logs",
    level=logging.DEBUG,
    console_output=True
)

class UserService:
    """用户服务类"""
    
    def __init__(self, db: Session = None):
        """初始化用户服务
        
        Args:
            db (Session, optional): 数据库会话实例
        """
        self.db = db or session
        user_logger.debug("UserService初始化完成")
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """通过用户名获取用户
        
        Args:
            username (str): 用户名
            
        Returns:
            Optional[User]: 用户对象
        """
        try:
            user_logger.debug(f"尝试通过用户名获取用户: {username}")
            user = (self.db.query(User)
                   .filter(User.username == username)
                   .first())
            if user:
                # 手动加载角色关系
                self.db.refresh(user)
            return user
        except Exception as e:
            user_logger.error(f"通过用户名获取用户失败: {str(e)}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """通过用户ID获取用户
        
        Args:
            user_id (int): 用户ID
            
        Returns:
            Optional[User]: 用户对象
        """
        try:
            user_logger.debug(f"尝试通过ID获取用户: {user_id}")
            user = (self.db.query(User)
                   .filter(User.id == user_id)
                   .first())
            if user:
                # 手动加载关系
                self.db.refresh(user)
            return user
        except Exception as e:
            user_logger.error(f"通过ID获取用户失败: {str(e)}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        try:
            user_logger.debug(f"尝试通过邮箱获取用户: {email}")
            user = (self.db.query(User)
                   .filter(User.email == email)
                   .first())
            if user:
                # 手动加载关系
                self.db.refresh(user)
                user_logger.debug(f"成功获取到用户: {user.username}")
            else:
                user_logger.debug(f"未找到邮箱为{email}的用户")
            return user
        except Exception as e:
            user_logger.error(f"通过邮箱获取用户失败: {str(e)}")
            return None
    
    def create_user(self, username: str, email: str, password: str, 
                   department_id: Optional[int] = None,
                   role_ids: Optional[List[int]] = None) -> User:
        """创建用户"""
        # 检查用户名和邮箱是否已存在
        existing_user = self.get_user_by_username(username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        
        existing_email = self.get_user_by_email(email)
        if existing_email:
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
        user_logger.debug(f"开始验证用户 {user.username} 的密码")
        result = verify_password(password, user.password_hash)
        if result:
            user_logger.debug(f"用户 {user.username} 密码验证成功")
        else:
            user_logger.debug(f"用户 {user.username} 密码验证失败")
        return result
    
    def get_user_roles(self, user_id: int) -> List[Role]:
        """获取用户角色列表
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[Role]: 角色列表
        """
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return []
            return user.roles
        except Exception as e:
            user_logger.error(f"获取用户角色失败: {str(e)}")
            return []

    def get_user_permissions(self, user_id: int) -> List[Permission]:
        """获取用户权限列表
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[Permission]: 权限列表
        """
        try:
            permissions = set()
            user = (self.db.query(User)
                   .options(joinedload(User.roles)
                          .joinedload(Role.permissions))
                   .filter(User.id == user_id)
                   .first())
            
            if user:
                for role in user.roles:
                    permissions.update(role.permissions)
                    
            return list(permissions)
        except Exception as e:
            user_logger.error(f"获取用户权限失败: {str(e)}")
            return []

class RoleService:
    """角色服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        user_logger.debug("RoleService初始化完成")
    
    def get_role_by_id(self, role_id: int) -> Optional[Role]:
        """根据ID获取角色"""
        user_logger.debug(f"尝试通过ID获取角色: {role_id}")
        role = (self.db.query(Role)
               .options(joinedload(Role.permissions))
               .filter(Role.id == role_id)
               .first())
        if role:
            user_logger.debug(f"成功获取到角色: {role.name}")
        else:
            user_logger.debug(f"未找到ID为{role_id}的角色")
        return role
    
    def get_role_by_name(self, name: str) -> Optional[Role]:
        """根据名称获取角色"""
        user_logger.debug(f"尝试通过名称获取角色: {name}")
        role = (self.db.query(Role)
               .options(joinedload(Role.permissions))
               .filter(Role.name == name)
               .first())
        if role:
            user_logger.debug(f"成功获取到角色: {role.name}")
        else:
            user_logger.debug(f"未找到名称为{name}的角色")
        return role
    
    def create_role(self, name: str, description: Optional[str] = None,
                   permission_ids: Optional[List[int]] = None) -> Role:
        """创建角色"""
        user_logger.debug(f"开始创建角色: {name}")
        # 检查角色名是否已存在
        existing_role = self.get_role_by_name(name)
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="角色名已存在"
            )
        
        # 创建角色
        role = Role(
            name=name,
            description=description
        )
        
        # 添加权限
        if permission_ids:
            permissions = self.db.query(Permission).filter(Permission.id.in_(permission_ids)).all()
            role.permissions = permissions
            user_logger.debug(f"为角色 {name} 添加了 {len(permissions)} 个权限")
        
        try:
            self.db.add(role)
            self.db.commit()
            self.db.refresh(role)
            user_logger.debug(f"角色 {name} 创建成功")
            return role
        except IntegrityError:
            self.db.rollback()
            user_logger.error(f"创建角色 {name} 失败")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="创建角色失败"
            )
    
    def update_role(self, role_id: int, name: Optional[str] = None,
                   description: Optional[str] = None,
                   permission_ids: Optional[List[int]] = None) -> Role:
        """更新角色"""
        user_logger.debug(f"开始更新角色ID: {role_id}")
        # 获取角色
        role = self.get_role_by_id(role_id)
        if not role:
            user_logger.error(f"未找到ID为{role_id}的角色")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        
        # 如果要更新名称，检查新名称是否已存在
        if name and name != role.name:
            existing_role = self.get_role_by_name(name)
            if existing_role:
                user_logger.error(f"角色名 {name} 已存在")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="角色名已存在"
                )
            role.name = name
            user_logger.debug(f"角色名更新为: {name}")
        
        # 更新描述
        if description is not None:
            role.description = description
            user_logger.debug(f"角色描述已更新")
        
        # 更新权限
        if permission_ids is not None:
            permissions = self.db.query(Permission).filter(Permission.id.in_(permission_ids)).all()
            role.permissions = permissions
            user_logger.debug(f"角色权限已更新，现有 {len(permissions)} 个权限")
        
        try:
            self.db.commit()
            self.db.refresh(role)
            user_logger.debug(f"角色 {role.name} 更新成功")
            return role
        except IntegrityError:
            self.db.rollback()
            user_logger.error(f"更新角色 {role.name} 失败")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="更新角色失败"
            )
    
    def delete_role(self, role_id: int) -> None:
        """删除角色"""
        user_logger.debug(f"开始删除角色ID: {role_id}")
        role = self.get_role_by_id(role_id)
        if not role:
            user_logger.error(f"未找到ID为{role_id}的角色")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        
        try:
            self.db.delete(role)
            self.db.commit()
            user_logger.debug(f"角色 {role.name} 删除成功")
        except IntegrityError:
            self.db.rollback()
            user_logger.error(f"删除角色 {role.name} 失败")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="删除角色失败"
            )
    
    def get_role_permissions(self, role_id: int) -> List[Permission]:
        """获取角色的权限列表"""
        user_logger.debug(f"开始获取角色ID {role_id} 的权限")
        role = self.get_role_by_id(role_id)
        if not role:
            user_logger.error(f"未找到ID为{role_id}的角色")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        
        permissions = role.permissions
        user_logger.debug(f"角色 {role.name} 有 {len(permissions)} 个权限")
        return permissions

class DepartmentService:
    """部门服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        user_logger.debug("DepartmentService初始化")

    def get_department_by_id(self, department_id: int) -> Optional[Department]:
        """根据ID获取部门"""
        user_logger.debug(f"开始获取部门ID: {department_id}")
        department = self.db.query(Department).filter(Department.id == department_id).first()
        
        if department:
            user_logger.debug(f"找到部门: {department.name}")
        else:
            user_logger.debug(f"未找到ID为{department_id}的部门")
        return department

    def get_department_by_name(self, name: str) -> Optional[Department]:
        """根据名称获取部门"""
        user_logger.debug(f"开始获取部门名称: {name}")
        department = self.db.query(Department).filter(Department.name == name).first()
        
        if department:
            user_logger.debug(f"找到部门: {department.name}")
        else:
            user_logger.debug(f"未找到名为{name}的部门")
        return department

    def create_department(self, name: str, description: Optional[str] = None,
                        parent_id: Optional[int] = None) -> Department:
        """创建部门"""
        user_logger.debug(f"开始创建部门: {name}")
        # 检查部门名是否已存在
        existing_department = self.get_department_by_name(name)
        if existing_department:
            user_logger.error(f"部门名 {name} 已存在")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="部门名已存在"
            )
        
        # 如果指定了父部门，检查父部门是否存在
        if parent_id:
            parent_department = self.get_department_by_id(parent_id)
            if not parent_department:
                user_logger.error(f"未找到父部门ID: {parent_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="父部门不存在"
                )
        
        # 创建新部门
        department = Department(
            name=name,
            description=description,
            parent_id=parent_id
        )
        
        try:
            self.db.add(department)
            self.db.commit()
            self.db.refresh(department)
            user_logger.debug(f"部门 {name} 创建成功")
            return department
        except IntegrityError:
            self.db.rollback()
            user_logger.error(f"创建部门 {name} 失败")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="创建部门失败"
            )

    def update_department(self, department_id: int, name: Optional[str] = None,
                        description: Optional[str] = None,
                        parent_id: Optional[int] = None) -> Department:
        """更新部门"""
        user_logger.debug(f"开始更新部门ID: {department_id}")
        # 获取部门
        department = self.get_department_by_id(department_id)
        if not department:
            user_logger.error(f"未找到ID为{department_id}的部门")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="部门不存在"
            )
        
        # 如果要更新名称，检查新名称是否已存在
        if name and name != department.name:
            existing_department = self.get_department_by_name(name)
            if existing_department:
                user_logger.error(f"部门名 {name} 已存在")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="部门名已存在"
                )
            department.name = name
            user_logger.debug(f"部门名更新为: {name}")
        
        # 更新描述
        if description is not None:
            department.description = description
            user_logger.debug(f"部门描述已更新")
        
        # 更新父部门
        if parent_id is not None:
            if parent_id != 0:  # parent_id为0表示设置为顶级部门
                parent_department = self.get_department_by_id(parent_id)
                if not parent_department:
                    user_logger.error(f"未找到父部门ID: {parent_id}")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="父部门不存在"
                    )
            department.parent_id = parent_id if parent_id != 0 else None
            user_logger.debug(f"父部门ID更新为: {parent_id}")
        
        try:
            self.db.commit()
            self.db.refresh(department)
            user_logger.debug(f"部门 {department.name} 更新成功")
            return department
        except IntegrityError:
            self.db.rollback()
            user_logger.error(f"更新部门 {department.name} 失败")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="更新部门失败"
            )

    def delete_department(self, department_id: int) -> None:
        """删除部门"""
        user_logger.debug(f"开始删除部门ID: {department_id}")
        department = self.get_department_by_id(department_id)
        if not department:
            user_logger.error(f"未找到ID为{department_id}的部门")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="部门不存在"
            )
        
        # 检查是否有子部门
        has_children = self.db.query(Department).filter(Department.parent_id == department_id).first() is not None
        if has_children:
            user_logger.error(f"部门 {department.name} 存在子部门，无法删除")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="存在子部门，无法删除"
            )
        
        # 检查是否有用户
        has_users = self.db.query(User).filter(User.department_id == department_id).first() is not None
        if has_users:
            user_logger.error(f"部门 {department.name} 存在用户，无法删除")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="部门中存在用户，无法删除"
            )
        
        try:
            self.db.delete(department)
            self.db.commit()
            user_logger.debug(f"部门 {department.name} 删除成功")
        except IntegrityError:
            self.db.rollback()
            user_logger.error(f"删除部门 {department.name} 失败")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="删除部门失败"
            )

    def get_department_tree(self) -> List[Dict]:
        """获取部门树结构"""
        user_logger.debug("开始获取部门树结构")
        # 获取所有部门
        departments = self.db.query(Department).all()
        
        # 构建部门树
        department_dict = {dept.id: dept for dept in departments}
        tree = []
        
        for dept in departments:
            if dept.parent_id is None:
                tree.append(self._build_department_tree(dept, department_dict))
        
        user_logger.debug(f"部门树构建完成，共 {len(tree)} 个顶级部门")
        return tree

    def _build_department_tree(self, department: Department,
                             department_dict: Dict[int, Department]) -> Dict:
        """递归构建部门树"""
        result = {
            "id": department.id,
            "name": department.name,
            "description": department.description,
            "children": []
        }
        
        # 查找子部门
        for dept_id, dept in department_dict.items():
            if dept.parent_id == department.id:
                result["children"].append(
                    self._build_department_tree(dept, department_dict)
                )
        
        return result 