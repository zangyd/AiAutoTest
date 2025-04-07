"""
项目路由模块

处理项目相关的API路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.auth.jwt import get_current_user
from ...services.project import ProjectService
from .schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectList
)
from ...config.constants import ProjectStatus

router = APIRouter()


@router.post("/", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建项目"""
    return await ProjectService.create_project(
        db=db,
        name=project.name,
        description=project.description,
        created_by=current_user.id
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取项目详情"""
    return await ProjectService.get_project(db, project_id)


@router.get("/", response_model=ProjectList)
async def get_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取项目列表"""
    projects = await ProjectService.get_projects(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        search=search
    )
    return {
        "total": len(projects),
        "items": projects
    }


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新项目"""
    return await ProjectService.update_project(
        db=db,
        project_id=project_id,
        user_id=current_user.id,
        **project.dict(exclude_unset=True)
    )


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """删除项目"""
    await ProjectService.delete_project(
        db=db,
        project_id=project_id,
        user_id=current_user.id
    )
    return {"message": "Project deleted successfully"}


@router.put("/{project_id}/status", response_model=ProjectResponse)
async def change_project_status(
    project_id: int,
    status: ProjectStatus,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """修改项目状态"""
    return await ProjectService.change_project_status(
        db=db,
        project_id=project_id,
        user_id=current_user.id,
        status=status
    ) 