"""
测试路由模块

处理测试用例和测试运行相关的API路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.auth.jwt import get_current_user
from ...services.test import TestService
from .schemas import (
    TestCaseCreate,
    TestCaseUpdate,
    TestCaseResponse,
    TestCaseList,
    TestRunCreate,
    TestRunResponse,
    TestRunList,
    TestResultCreate,
    TestResultResponse,
    TestResultList
)
from ...config.constants import TestStatus, TestType, TestPriority

router = APIRouter()


# 测试用例路由
@router.post("/cases", response_model=TestCaseResponse)
async def create_test_case(
    test_case: TestCaseCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建测试用例"""
    return await TestService.create_test_case(
        db=db,
        project_id=test_case.project_id,
        name=test_case.name,
        description=test_case.description,
        type=test_case.type,
        priority=test_case.priority,
        steps=test_case.steps,
        test_data=test_case.test_data,
        prerequisites=test_case.prerequisites,
        created_by=current_user.id
    )


@router.get("/cases/{test_case_id}", response_model=TestCaseResponse)
async def get_test_case(
    test_case_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取测试用例详情"""
    return await TestService.get_test_case(db, test_case_id)


@router.get("/projects/{project_id}/cases", response_model=TestCaseList)
async def get_test_cases(
    project_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    type: Optional[TestType] = None,
    priority: Optional[TestPriority] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取测试用例列表"""
    test_cases = await TestService.get_test_cases(
        db=db,
        project_id=project_id,
        skip=skip,
        limit=limit,
        search=search,
        type=type,
        priority=priority
    )
    return {
        "total": len(test_cases),
        "items": test_cases
    }


@router.put("/cases/{test_case_id}", response_model=TestCaseResponse)
async def update_test_case(
    test_case_id: int,
    test_case: TestCaseUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新测试用例"""
    return await TestService.update_test_case(
        db=db,
        test_case_id=test_case_id,
        user_id=current_user.id,
        **test_case.dict(exclude_unset=True)
    )


@router.delete("/cases/{test_case_id}")
async def delete_test_case(
    test_case_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """删除测试用例"""
    await TestService.delete_test_case(
        db=db,
        test_case_id=test_case_id,
        user_id=current_user.id
    )
    return {"message": "Test case deleted successfully"}


# 测试运行路由
@router.post("/runs", response_model=TestRunResponse)
async def create_test_run(
    test_run: TestRunCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建测试运行"""
    return await TestService.create_test_run(
        db=db,
        project_id=test_run.project_id,
        name=test_run.name,
        description=test_run.description,
        environment=test_run.environment,
        started_by=current_user.id
    )


@router.get("/runs/{test_run_id}", response_model=TestRunResponse)
async def get_test_run(
    test_run_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取测试运行详情"""
    return await TestService.get_test_run(db, test_run_id)


@router.get("/projects/{project_id}/runs", response_model=TestRunList)
async def get_test_runs(
    project_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取测试运行列表"""
    test_runs = await TestService.get_test_runs(
        db=db,
        project_id=project_id,
        skip=skip,
        limit=limit
    )
    return {
        "total": len(test_runs),
        "items": test_runs
    }


# 测试结果路由
@router.post("/results", response_model=TestResultResponse)
async def create_test_result(
    test_result: TestResultCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建测试结果"""
    return await TestService.create_test_result(
        db=db,
        test_run_id=test_result.test_run_id,
        test_case_id=test_result.test_case_id,
        status=test_result.status,
        output=test_result.output,
        error_message=test_result.error_message,
        stack_trace=test_result.stack_trace,
        test_data=test_result.test_data
    )


@router.get("/runs/{test_run_id}/results", response_model=TestResultList)
async def get_test_results(
    test_run_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[TestStatus] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取测试结果列表"""
    test_results = await TestService.get_test_results(
        db=db,
        test_run_id=test_run_id,
        skip=skip,
        limit=limit,
        status=status
    )
    return {
        "total": len(test_results),
        "items": test_results
    } 