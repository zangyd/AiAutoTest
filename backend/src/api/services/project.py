"""
项目服务模块

处理项目相关的业务逻辑
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..models.project import Project
from ..models.user import User
from ..core.exceptions import NotFoundError, PermissionError
from ..config.constants import ProjectStatus


class ProjectService:
    """项目服务"""

    @staticmethod
    async def create_project(
        db: Session,
        name: str,
        description: Optional[str],
        created_by: int
    ) -> Project:
        """创建项目"""
        project = Project(
            name=name,
            description=description,
            created_by=created_by,
            status=ProjectStatus.DRAFT
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    async def get_project(db: Session, project_id: int) -> Project:
        """获取项目"""
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise NotFoundError(f"Project {project_id} not found")
        return project

    @staticmethod
    async def get_projects(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None
    ) -> List[Project]:
        """获取项目列表"""
        query = db.query(Project)
        
        # 搜索
        if search:
            query = query.filter(
                or_(
                    Project.name.ilike(f"%{search}%"),
                    Project.description.ilike(f"%{search}%")
                )
            )
        
        # 分页
        return query.offset(skip).limit(limit).all()

    @staticmethod
    async def update_project(
        db: Session,
        project_id: int,
        user_id: int,
        **kwargs
    ) -> Project:
        """更新项目"""
        project = await ProjectService.get_project(db, project_id)
        
        # 检查权限
        if project.created_by != user_id:
            raise PermissionError("Only project creator can update project")
        
        # 更新字段
        for key, value in kwargs.items():
            if hasattr(project, key):
                setattr(project, key, value)
        
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    async def delete_project(
        db: Session,
        project_id: int,
        user_id: int
    ) -> None:
        """删除项目"""
        project = await ProjectService.get_project(db, project_id)
        
        # 检查权限
        if project.created_by != user_id:
            raise PermissionError("Only project creator can delete project")
        
        db.delete(project)
        db.commit()

    @staticmethod
    async def change_project_status(
        db: Session,
        project_id: int,
        user_id: int,
        status: ProjectStatus
    ) -> Project:
        """修改项目状态"""
        project = await ProjectService.get_project(db, project_id)
        
        # 检查权限
        if project.created_by != user_id:
            raise PermissionError("Only project creator can change project status")
        
        project.status = status
        db.commit()
        db.refresh(project)
        return project 