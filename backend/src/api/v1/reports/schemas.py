"""
报告模型模块

定义测试报告相关的响应模型
"""
from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

from ...config.constants import TestStatus


class TestCaseResult(BaseModel):
    """测试用例结果模型"""
    id: int
    name: str
    status: TestStatus
    duration: Optional[int] = None
    error_message: Optional[str] = None


class TestRunSummaryResponse(BaseModel):
    """测试运行摘要响应模型"""
    id: int
    name: str
    environment: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration: Optional[int] = None
    total_cases: int
    passed_cases: int
    failed_cases: int
    error_cases: int
    skipped_cases: int
    success_rate: float

    class Config:
        from_attributes = True


class TestRunDetailResponse(TestRunSummaryResponse):
    """测试运行详细信息响应模型"""
    results: List[TestCaseResult]


class DailyStatistics(BaseModel):
    """每日统计数据模型"""
    date: str
    total_runs: int
    total_cases: int
    passed_cases: int
    failed_cases: int
    error_cases: int
    skipped_cases: int
    success_rate: float


class ProjectStatisticsResponse(BaseModel):
    """项目统计信息响应模型"""
    project_id: int
    total_test_cases: int
    total_test_runs: int
    latest_success_rate: float
    average_success_rate: float
    total_execution_time: int
    daily_statistics: List[DailyStatistics]

    class Config:
        from_attributes = True


class TrendPoint(BaseModel):
    """趋势点模型"""
    date: str
    value: float


class TrendAnalysisResponse(BaseModel):
    """趋势分析响应模型"""
    success_rate_trend: List[TrendPoint]
    execution_time_trend: List[TrendPoint]
    test_case_count_trend: List[TrendPoint]

    class Config:
        from_attributes = True 