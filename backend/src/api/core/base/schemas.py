"""
基础响应模式定义
"""
from datetime import datetime, timezone
from typing import Generic, TypeVar, Optional, Any, Dict, List
from pydantic import BaseModel, Field, validator, ConfigDict

# 定义泛型类型变量
T = TypeVar('T')

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

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda dt: dt.isoformat()
        }
    )

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