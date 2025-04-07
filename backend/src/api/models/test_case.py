"""
测试用例模型模块

定义测试用例相关的数据模型
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Enum, JSON
from sqlalchemy.orm import relationship

from ..core.database import Base
from ..config.constants import TestPriority, TestType


class TestCase(Base):
    """测试用例模型"""
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    type = Column(Enum(TestType), nullable=False)
    priority = Column(Enum(TestPriority), default=TestPriority.MEDIUM)
    project_id = Column(Integer, ForeignKey("projects.id"))
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 测试步骤和预期结果
    steps = Column(JSON)  # [{"step": "步骤1", "expected": "预期结果1"}, ...]
    
    # 测试数据
    test_data = Column(JSON)  # {"key1": "value1", "key2": "value2"}
    
    # 环境要求
    prerequisites = Column(Text)
    
    # 关系
    project = relationship("Project", back_populates="test_cases")
    creator = relationship("User", back_populates="test_cases")
    test_results = relationship("TestResult", back_populates="test_case")

    def __repr__(self):
        return f"<TestCase {self.name}>" 