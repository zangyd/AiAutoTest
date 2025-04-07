"""
报告服务模块

处理测试报告相关的业务逻辑
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..models.report import TestRun, TestResult
from ..core.exceptions import NotFoundError
from ..config.constants import TestStatus


class ReportService:
    """报告服务"""

    @staticmethod
    async def get_test_run_summary(db: Session, test_run_id: int) -> Dict[str, Any]:
        """获取测试运行摘要"""
        test_run = db.query(TestRun).filter(TestRun.id == test_run_id).first()
        if not test_run:
            raise NotFoundError(f"Test run {test_run_id} not found")
        
        return {
            "id": test_run.id,
            "name": test_run.name,
            "description": test_run.description,
            "environment": test_run.environment,
            "started_at": test_run.started_at,
            "completed_at": test_run.completed_at,
            "duration": (
                int((test_run.completed_at - test_run.started_at).total_seconds())
                if test_run.completed_at
                else None
            ),
            "statistics": {
                "total": test_run.total_cases,
                "passed": test_run.passed_cases,
                "failed": test_run.failed_cases,
                "error": test_run.error_cases,
                "skipped": test_run.skipped_cases,
                "success_rate": (
                    round(test_run.passed_cases / test_run.total_cases * 100, 2)
                    if test_run.total_cases > 0
                    else 0
                )
            }
        }

    @staticmethod
    async def get_test_run_details(
        db: Session,
        test_run_id: int,
        status: Optional[TestStatus] = None
    ) -> Dict[str, Any]:
        """获取测试运行详情"""
        # 获取测试运行摘要
        summary = await ReportService.get_test_run_summary(db, test_run_id)
        
        # 查询测试结果
        query = db.query(TestResult).filter(TestResult.test_run_id == test_run_id)
        if status:
            query = query.filter(TestResult.status == status)
        
        results = []
        for result in query.all():
            results.append({
                "id": result.id,
                "test_case": {
                    "id": result.test_case.id,
                    "name": result.test_case.name,
                    "type": result.test_case.type,
                    "priority": result.test_case.priority
                },
                "status": result.status,
                "started_at": result.started_at,
                "completed_at": result.completed_at,
                "duration": result.duration,
                "output": result.output,
                "error_message": result.error_message,
                "stack_trace": result.stack_trace,
                "test_data": result.test_data
            })
        
        return {
            "summary": summary,
            "results": results
        }

    @staticmethod
    async def get_project_statistics(
        db: Session,
        project_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """获取项目统计信息"""
        # 构建查询
        query = db.query(TestRun).filter(TestRun.project_id == project_id)
        
        if start_date:
            query = query.filter(TestRun.started_at >= start_date)
        if end_date:
            query = query.filter(TestRun.started_at <= end_date)
        
        test_runs = query.order_by(desc(TestRun.started_at)).all()
        
        # 统计数据
        total_runs = len(test_runs)
        total_cases = sum(run.total_cases for run in test_runs)
        passed_cases = sum(run.passed_cases for run in test_runs)
        failed_cases = sum(run.failed_cases for run in test_runs)
        error_cases = sum(run.error_cases for run in test_runs)
        skipped_cases = sum(run.skipped_cases for run in test_runs)
        
        return {
            "total_runs": total_runs,
            "total_cases": total_cases,
            "statistics": {
                "passed": passed_cases,
                "failed": failed_cases,
                "error": error_cases,
                "skipped": skipped_cases,
                "success_rate": (
                    round(passed_cases / total_cases * 100, 2)
                    if total_cases > 0
                    else 0
                )
            },
            "trend": [
                {
                    "id": run.id,
                    "name": run.name,
                    "started_at": run.started_at,
                    "total_cases": run.total_cases,
                    "passed_cases": run.passed_cases,
                    "success_rate": (
                        round(run.passed_cases / run.total_cases * 100, 2)
                        if run.total_cases > 0
                        else 0
                    )
                }
                for run in test_runs
            ]
        } 