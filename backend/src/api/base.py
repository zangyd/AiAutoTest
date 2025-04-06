from datetime import datetime, timezone
from enum import Enum
from typing import Generic, TypeVar, Optional, Any, Dict, List
from fastapi import APIRouter, Query, Path, Body, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator, conint

# 定义泛型类型变量
T = TypeVar('T')

# 标准化状态枚举
class StatusEnum(str, Enum):
    """状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETED = "deleted"

# 标准化优先级枚举
class PriorityEnum(str, Enum):
    """优先级枚举"""
    P0 = "P0"  # 最高优先级
    P1 = "P1"  # 高优先级
    P2 = "P2"  # 中优先级
    P3 = "P3"  # 低优先级
    P4 = "P4"  # 最低优先级

class DateTimeModelMixin(BaseModel):
    """时间模型混入类"""
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class FilterParams(BaseModel):
    """过滤参数模型"""
    field: str
    operator: str
    value: Any

class SortParams(BaseModel):
    """排序参数模型"""
    field: str
    order: str = Field(default="asc", pattern="^(asc|desc)$")

class QueryParams(BaseModel):
    """查询参数基础模型"""
    filter: Optional[List[FilterParams]] = None
    sort: Optional[List[SortParams]] = None
    search: Optional[str] = None

class PaginationParams(BaseModel):
    """分页参数模型"""
    page: int = Field(default=1, ge=1, description="当前页码")
    size: int = Field(default=10, ge=1, le=100, description="每页大小")

    @validator('size')
    def validate_size(cls, v):
        if v > 100:
            raise ValueError("每页大小不能超过100")
        return v

class ResponseModel(BaseModel, Generic[T]):
    """通用响应模型"""
    code: int = Field(default=200, description="响应状态码")
    message: str = Field(default="success", description="响应消息")
    data: Optional[T] = Field(default=None, description="响应数据")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="响应时间")
    request_id: Optional[str] = Field(default=None, description="请求追踪ID")

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class PageModel(BaseModel, Generic[T]):
    """分页响应模型"""
    items: List[T] = Field(description="数据列表")
    total: int = Field(description="总记录数")
    page: int = Field(description="当前页码")
    size: int = Field(description="每页大小")
    pages: int = Field(description="总页数")

    @validator('pages')
    def calculate_pages(cls, v, values):
        if 'total' in values and 'size' in values:
            return (values['total'] + values['size'] - 1) // values['size']
        return v

class ErrorModel(BaseModel):
    """错误响应模型"""
    code: int = Field(description="错误码")
    message: str = Field(description="错误消息")
    detail: Optional[Any] = Field(default=None, description="错误详情")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="错误发生时间")

# 创建主路由
api_router = APIRouter()

# 导入并注册子路由
from .v1 import users, auth

api_router.include_router(users.router, prefix="/v1/users", tags=["用户"])
api_router.include_router(auth.router, prefix="/v1", tags=["认证"])

# 健康检查
@api_router.get(
    "/health",
    response_model=ResponseModel[Dict[str, Any]],
    summary="健康检查接口",
    description="用于检查API服务的健康状态",
    responses={
        200: {
            "description": "服务正常",
            "content": {
                "application/json": {
                    "example": {
                        "code": 200,
                        "message": "success",
                        "data": {
                            "status": "ok",
                            "timestamp": "2024-04-05T10:00:00Z"
                        }
                    }
                }
            }
        }
    }
)
async def health_check():
    """
    健康检查接口
    
    返回:
        - status: 服务状态
        - timestamp: 当前时间
    """
    return ResponseModel(
        data={
            "status": "ok",
            "timestamp": datetime.now(timezone.utc)
        }
    ) 