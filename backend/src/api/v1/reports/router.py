"""
报告路由模块

处理测试报告相关的API路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.auth.jwt import get_current_user
from ...services.report import ReportService
from .schemas import (
    TestRunSummaryResponse,
    TestRunDetailResponse,
    ProjectStatisticsResponse,
    TrendAnalysisResponse
)

router = APIRouter()


@router.get("/runs/{test_run_id}/summary", response_model=TestRunSummaryResponse)
async def get_test_run_summary(
    test_run_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取测试运行摘要"""
    return await ReportService.get_test_run_summary(db, test_run_id)


@router.get("/runs/{test_run_id}/detail", response_model=TestRunDetailResponse)
async def get_test_run_detail(
    test_run_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取测试运行详细信息"""
    return await ReportService.get_test_run_detail(db, test_run_id)


@router.get("/projects/{project_id}/statistics", response_model=ProjectStatisticsResponse)
async def get_project_statistics(
    project_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取项目统计信息"""
    return await ReportService.get_project_statistics(
        db=db,
        project_id=project_id,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/projects/{project_id}/trends", response_model=TrendAnalysisResponse)
async def get_trend_analysis(
    project_id: int,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取趋势分析数据"""
    return await ReportService.get_trend_analysis(
        db=db,
        project_id=project_id,
        days=days
    ) 