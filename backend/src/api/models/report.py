"""
测试报告模型模块

定义测试报告相关的数据模型
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Enum, JSON
from sqlalchemy.orm import relationship

from ..core.database import Base
from ..config.constants import TestStatus


class TestRun(Base):
    """测试运行模型"""
    __tablename__ = "test_runs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    project_id = Column(Integer, ForeignKey("projects.id"))
    started_by = Column(Integer, ForeignKey("users.id"))
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    environment = Column(String(50))  # 测试环境
    
    # 统计信息
    total_cases = Column(Integer, default=0)
    passed_cases = Column(Integer, default=0)
    failed_cases = Column(Integer, default=0)
    error_cases = Column(Integer, default=0)
    skipped_cases = Column(Integer, default=0)
    
    # 关系
    project = relationship("Project", back_populates="test_runs")
    starter = relationship("User", back_populates="test_runs")
    test_results = relationship("TestResult", back_populates="test_run")

    def __repr__(self):
        return f"<TestRun {self.name}>"


class TestResult(Base):
    """测试结果模型"""
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, index=True)
    test_run_id = Column(Integer, ForeignKey("test_runs.id"))
    test_case_id = Column(Integer, ForeignKey("test_cases.id"))
    status = Column(Enum(TestStatus), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    duration = Column(Integer)  # 执行时长（秒）
    
    # 测试输出
    output = Column(Text)  # 测试输出日志
    error_message = Column(Text)  # 错误信息
    stack_trace = Column(Text)  # 堆栈跟踪
    
    # 测试数据
    test_data = Column(JSON)  # 实际使用的测试数据
    
    # 关系
    test_run = relationship("TestRun", back_populates="test_results")
    test_case = relationship("TestCase", back_populates="test_results")

    def __repr__(self):
        return f"<TestResult {self.id}>" 