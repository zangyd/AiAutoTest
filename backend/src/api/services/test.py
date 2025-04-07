"""
测试服务模块

处理测试用例和测试运行相关的业务逻辑
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..models.test_case import TestCase
from ..models.report import TestRun, TestResult
from ..core.exceptions import NotFoundError, PermissionError
from ..config.constants import TestStatus, TestPriority, TestType


class TestService:
    """测试服务"""

    @staticmethod
    async def create_test_case(
        db: Session,
        project_id: int,
        name: str,
        description: str,
        type: TestType,
        priority: TestPriority,
        steps: List[Dict[str, str]],
        test_data: Dict[str, Any],
        prerequisites: Optional[str],
        created_by: int
    ) -> TestCase:
        """创建测试用例"""
        test_case = TestCase(
            project_id=project_id,
            name=name,
            description=description,
            type=type,
            priority=priority,
            steps=steps,
            test_data=test_data,
            prerequisites=prerequisites,
            created_by=created_by
        )
        db.add(test_case)
        db.commit()
        db.refresh(test_case)
        return test_case

    @staticmethod
    async def get_test_case(db: Session, test_case_id: int) -> TestCase:
        """获取测试用例"""
        test_case = db.query(TestCase).filter(TestCase.id == test_case_id).first()
        if not test_case:
            raise NotFoundError(f"Test case {test_case_id} not found")
        return test_case

    @staticmethod
    async def get_test_cases(
        db: Session,
        project_id: int,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        type: Optional[TestType] = None,
        priority: Optional[TestPriority] = None
    ) -> List[TestCase]:
        """获取测试用例列表"""
        query = db.query(TestCase).filter(TestCase.project_id == project_id)
        
        # 搜索
        if search:
            query = query.filter(
                or_(
                    TestCase.name.ilike(f"%{search}%"),
                    TestCase.description.ilike(f"%{search}%")
                )
            )
        
        # 类型过滤
        if type:
            query = query.filter(TestCase.type == type)
        
        # 优先级过滤
        if priority:
            query = query.filter(TestCase.priority == priority)
        
        # 分页
        return query.offset(skip).limit(limit).all()

    @staticmethod
    async def update_test_case(
        db: Session,
        test_case_id: int,
        user_id: int,
        **kwargs
    ) -> TestCase:
        """更新测试用例"""
        test_case = await TestService.get_test_case(db, test_case_id)
        
        # 检查权限
        if test_case.created_by != user_id:
            raise PermissionError("Only test case creator can update test case")
        
        # 更新字段
        for key, value in kwargs.items():
            if hasattr(test_case, key):
                setattr(test_case, key, value)
        
        db.commit()
        db.refresh(test_case)
        return test_case

    @staticmethod
    async def delete_test_case(
        db: Session,
        test_case_id: int,
        user_id: int
    ) -> None:
        """删除测试用例"""
        test_case = await TestService.get_test_case(db, test_case_id)
        
        # 检查权限
        if test_case.created_by != user_id:
            raise PermissionError("Only test case creator can delete test case")
        
        db.delete(test_case)
        db.commit()

    @staticmethod
    async def create_test_run(
        db: Session,
        project_id: int,
        name: str,
        description: str,
        environment: str,
        started_by: int
    ) -> TestRun:
        """创建测试运行"""
        test_run = TestRun(
            project_id=project_id,
            name=name,
            description=description,
            environment=environment,
            started_by=started_by
        )
        db.add(test_run)
        db.commit()
        db.refresh(test_run)
        return test_run

    @staticmethod
    async def get_test_run(db: Session, test_run_id: int) -> TestRun:
        """获取测试运行"""
        test_run = db.query(TestRun).filter(TestRun.id == test_run_id).first()
        if not test_run:
            raise NotFoundError(f"Test run {test_run_id} not found")
        return test_run

    @staticmethod
    async def get_test_runs(
        db: Session,
        project_id: int,
        skip: int = 0,
        limit: int = 10
    ) -> List[TestRun]:
        """获取测试运行列表"""
        return (
            db.query(TestRun)
            .filter(TestRun.project_id == project_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    async def create_test_result(
        db: Session,
        test_run_id: int,
        test_case_id: int,
        status: TestStatus,
        output: Optional[str] = None,
        error_message: Optional[str] = None,
        stack_trace: Optional[str] = None,
        test_data: Optional[Dict[str, Any]] = None
    ) -> TestResult:
        """创建测试结果"""
        # 获取测试运行
        test_run = await TestService.get_test_run(db, test_run_id)
        
        # 创建测试结果
        test_result = TestResult(
            test_run_id=test_run_id,
            test_case_id=test_case_id,
            status=status,
            output=output,
            error_message=error_message,
            stack_trace=stack_trace,
            test_data=test_data,
            completed_at=datetime.utcnow()
        )
        
        # 计算执行时长
        test_result.duration = int(
            (test_result.completed_at - test_result.started_at).total_seconds()
        )
        
        # 更新测试运行统计信息
        test_run.total_cases += 1
        if status == TestStatus.PASSED:
            test_run.passed_cases += 1
        elif status == TestStatus.FAILED:
            test_run.failed_cases += 1
        elif status == TestStatus.ERROR:
            test_run.error_cases += 1
        elif status == TestStatus.SKIPPED:
            test_run.skipped_cases += 1
        
        db.add(test_result)
        db.commit()
        db.refresh(test_result)
        return test_result

    @staticmethod
    async def get_test_results(
        db: Session,
        test_run_id: int,
        skip: int = 0,
        limit: int = 10,
        status: Optional[TestStatus] = None
    ) -> List[TestResult]:
        """获取测试结果列表"""
        query = db.query(TestResult).filter(TestResult.test_run_id == test_run_id)
        
        # 状态过滤
        if status:
            query = query.filter(TestResult.status == status)
        
        # 分页
        return query.offset(skip).limit(limit).all() 