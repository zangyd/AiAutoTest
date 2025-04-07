"""
测试模型模块

定义测试用例、测试运行和测试结果相关的请求和响应模型
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from ...config.constants import TestStatus, TestType, TestPriority


# 测试用例模型
class TestCaseBase(BaseModel):
    """测试用例基础模型"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    type: TestType
    priority: TestPriority = TestPriority.MEDIUM
    steps: List[Dict[str, str]] = Field(
        ...,
        description="测试步骤列表，每个步骤包含step和expected字段"
    )
    test_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="测试数据"
    )
    prerequisites: Optional[str] = None


class TestCaseCreate(TestCaseBase):
    """测试用例创建模型"""
    project_id: int


class TestCaseUpdate(TestCaseBase):
    """测试用例更新模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    type: Optional[TestType] = None
    priority: Optional[TestPriority] = None
    steps: Optional[List[Dict[str, str]]] = None
    test_data: Optional[Dict[str, Any]] = None


class TestCaseResponse(TestCaseBase):
    """测试用例响应模型"""
    id: int
    project_id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TestCaseList(BaseModel):
    """测试用例列表响应模型"""
    total: int
    items: List[TestCaseResponse]


# 测试运行模型
class TestRunBase(BaseModel):
    """测试运行基础模型"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    environment: str = Field(..., min_length=1, max_length=50)


class TestRunCreate(TestRunBase):
    """测试运行创建模型"""
    project_id: int


class TestRunResponse(TestRunBase):
    """测试运行响应模型"""
    id: int
    project_id: int
    started_by: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_cases: int
    passed_cases: int
    failed_cases: int
    error_cases: int
    skipped_cases: int

    class Config:
        from_attributes = True


class TestRunList(BaseModel):
    """测试运行列表响应模型"""
    total: int
    items: List[TestRunResponse]


# 测试结果模型
class TestResultBase(BaseModel):
    """测试结果基础模型"""
    status: TestStatus
    output: Optional[str] = None
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    test_data: Optional[Dict[str, Any]] = None


class TestResultCreate(TestResultBase):
    """测试结果创建模型"""
    test_run_id: int
    test_case_id: int


class TestResultResponse(TestResultBase):
    """测试结果响应模型"""
    id: int
    test_run_id: int
    test_case_id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration: Optional[int] = None

    class Config:
        from_attributes = True


class TestResultList(BaseModel):
    """测试结果列表响应模型"""
    total: int
    items: List[TestResultResponse] 