"""
基础工具函数
"""
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
import re
from fastapi import HTTPException, status

def generate_uuid() -> str:
    """生成UUID"""
    return str(uuid.uuid4())

def generate_request_id() -> str:
    """生成请求ID"""
    return f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{generate_uuid()[:8]}"

def hash_password(password: str) -> str:
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """验证手机号格式"""
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))

def format_datetime(dt: datetime) -> str:
    """格式化日期时间"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def parse_query_params(
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """解析查询参数"""
    query = {}
    for key, value in params.items():
        if value is not None:
            if isinstance(value, list):
                query[key] = {"$in": value}
            else:
                query[key] = value
    return query

def validate_sort_field(field: str, allowed_fields: List[str]) -> None:
    """验证排序字段"""
    if field not in allowed_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sort field: {field}. Allowed fields: {', '.join(allowed_fields)}"
        )

def format_file_size(size: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"

def safe_int(value: Any, default: int = 0) -> int:
    """安全转换整数"""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

def safe_float(value: Any, default: float = 0.0) -> float:
    """安全转换浮点数"""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """截断字符串"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """合并字典"""
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result

def filter_none_values(data: Dict) -> Dict:
    """过滤字典中的None值"""
    return {k: v for k, v in data.items() if v is not None}

def validate_json_data(data: Dict, required_fields: List[str]) -> None:
    """验证JSON数据"""
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required fields: {', '.join(missing_fields)}"
        ) 