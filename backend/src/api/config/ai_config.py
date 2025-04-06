"""
AI相关配置
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict

class LLMConfig(BaseModel):
    """LLM模型配置"""
    # 模型基础配置
    model_name: str = Field(
        default="deepseek-coder",
        description="模型名称"
    )
    model_version: str = Field(
        default="latest",
        description="模型版本"
    )
    model_path: str = Field(
        default="models/deepseek-coder",
        description="模型路径"
    )
    
    # 推理配置
    max_tokens: int = Field(
        default=2048,
        description="最大token数"
    )
    temperature: float = Field(
        default=0.7,
        description="温度参数"
    )
    top_p: float = Field(
        default=0.9,
        description="top-p采样参数"
    )
    
    # 批处理配置
    batch_size: int = Field(
        default=4,
        description="批处理大小"
    )
    max_batch_tokens: int = Field(
        default=8192,
        description="最大批处理token数"
    )
    
    # 资源配置
    device: str = Field(
        default="cuda",
        description="运行设备"
    )
    num_gpus: int = Field(
        default=1,
        description="GPU数量"
    )
    
    model_config = ConfigDict(title="LLM模型配置")

class VectorDBConfig(BaseModel):
    """向量数据库配置"""
    # 数据库配置
    db_type: str = Field(
        default="milvus",
        description="向量数据库类型"
    )
    host: str = Field(
        default="localhost",
        description="数据库主机"
    )
    port: int = Field(
        default=19530,
        description="数据库端口"
    )
    
    # 集合配置
    collection_name: str = Field(
        default="test_cases",
        description="集合名称"
    )
    dimension: int = Field(
        default=768,
        description="向量维度"
    )
    index_type: str = Field(
        default="IVF_FLAT",
        description="索引类型"
    )
    
    # 查询配置
    search_params: Dict[str, str] = Field(
        default={
            "metric_type": "L2",
            "params": {"nprobe": 10}
        },
        description="查询参数"
    )
    
    model_config = ConfigDict(title="向量数据库配置")

class PromptConfig(BaseModel):
    """提示词配置"""
    # 模板配置
    template_path: str = Field(
        default="prompts",
        description="模板路径"
    )
    default_language: str = Field(
        default="zh_CN",
        description="默认语言"
    )
    
    # 变量配置
    system_variables: Dict[str, str] = Field(
        default={
            "project_name": "AutoTest Platform",
            "version": "1.0.0"
        },
        description="系统变量"
    )
    
    # 优化配置
    max_history: int = Field(
        default=5,
        description="最大历史记录数"
    )
    context_window: int = Field(
        default=2048,
        description="上下文窗口大小"
    )
    
    model_config = ConfigDict(title="提示词配置")

class AIServiceConfig(BaseModel):
    """AI服务配置"""
    # 服务配置
    service_name: str = Field(
        default="ai_service",
        description="服务名称"
    )
    host: str = Field(
        default="localhost",
        description="服务主机"
    )
    port: int = Field(
        default=8001,
        description="服务端口"
    )
    
    # 限流配置
    rate_limit: int = Field(
        default=100,
        description="每分钟请求限制"
    )
    timeout: int = Field(
        default=30,
        description="请求超时时间(秒)"
    )
    
    # 缓存配置
    cache_enabled: bool = Field(
        default=True,
        description="启用缓存"
    )
    cache_ttl: int = Field(
        default=3600,
        description="缓存过期时间(秒)"
    )
    
    model_config = ConfigDict(title="AI服务配置")

# 导出配置实例
llm_config = LLMConfig()
vector_db_config = VectorDBConfig()
prompt_config = PromptConfig()
ai_service_config = AIServiceConfig() 