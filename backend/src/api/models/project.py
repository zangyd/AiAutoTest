"""
项目模型模块

定义项目相关的数据模型
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship

from ..core.database import Base
from ..config.constants import ProjectStatus


class Project(Base):
    """项目模型"""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.DRAFT)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    creator = relationship("User", back_populates="projects")
    test_cases = relationship("TestCase", back_populates="project")
    test_runs = relationship("TestRun", back_populates="project")

    def __repr__(self):
        return f"<Project {self.name}>" 