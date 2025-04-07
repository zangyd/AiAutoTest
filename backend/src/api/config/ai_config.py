"""
AI配置模块

管理所有AI相关的配置项，包括LLM、向量数据库、提示词等
"""
from core.config.base_settings import BaseAppSettings
from pydantic import Field
from typing import List, Optional, Dict

class AISettings(BaseAppSettings):
    """AI配置类"""
    
    # LLM配置
    LLM_MODEL: str = Field(default="deepseek-coder", description="LLM模型名称")
    LLM_TEMPERATURE: float = Field(default=0.7, description="生成温度")
    LLM_MAX_TOKENS: int = Field(default=2048, description="最大token数")
    LLM_TOP_P: float = Field(default=0.95, description="核采样阈值")
    LLM_FREQUENCY_PENALTY: float = Field(default=0.0, description="频率惩罚")
    LLM_PRESENCE_PENALTY: float = Field(default=0.0, description="存在惩罚")
    LLM_STOP_WORDS: List[str] = Field(default=["<|endoftext|>"], description="停止词")
    LLM_TIMEOUT: int = Field(default=30, description="请求超时时间")
    LLM_RETRY_COUNT: int = Field(default=3, description="重试次数")
    LLM_BATCH_SIZE: int = Field(default=5, description="批处理大小")
    
    # 向量数据库配置
    VECTOR_DB_TYPE: str = Field(default="milvus", description="向量数据库类型")
    VECTOR_DB_HOST: str = Field(default="localhost", description="向量数据库主机")
    VECTOR_DB_PORT: int = Field(default=19530, description="向量数据库端口")
    VECTOR_DB_USER: str = Field(default="root", description="向量数据库用户名")
    VECTOR_DB_PASSWORD: str = Field(default="", description="向量数据库密码")
    VECTOR_DB_COLLECTION: str = Field(default="embeddings", description="向量集合名称")
    VECTOR_DIMENSION: int = Field(default=768, description="向量维度")
    VECTOR_METRIC_TYPE: str = Field(default="L2", description="向量距离度量类型")
    VECTOR_INDEX_TYPE: str = Field(default="IVF_FLAT", description="向量索引类型")
    VECTOR_NLIST: int = Field(default=1024, description="向量索引聚类数")
    
    # 提示词配置
    PROMPT_TEMPLATE_DIR: str = Field(default="prompts", description="提示词模板目录")
    PROMPT_MAX_LENGTH: int = Field(default=2048, description="提示词最大长度")
    PROMPT_CACHE_SIZE: int = Field(default=1000, description="提示词缓存大小")
    PROMPT_VERSION_CONTROL: bool = Field(default=True, description="是否启用版本控制")
    
    # AI服务配置
    AI_SERVICE_TIMEOUT: int = Field(default=60, description="服务超时时间")
    AI_SERVICE_MAX_RETRIES: int = Field(default=3, description="最大重试次数")
    AI_SERVICE_CONCURRENT_REQUESTS: int = Field(default=10, description="并发请求数")
    AI_SERVICE_RATE_LIMIT: int = Field(default=100, description="每分钟请求限制")
    AI_SERVICE_CACHE_TTL: int = Field(default=3600, description="缓存过期时间")
    
    # 知识库配置
    KNOWLEDGE_BASE_DIR: str = Field(default="knowledge", description="知识库目录")
    KNOWLEDGE_FILE_TYPES: List[str] = Field(default=[".txt", ".md", ".pdf"], description="支持的文件类型")
    KNOWLEDGE_CHUNK_SIZE: int = Field(default=1000, description="文本分块大小")
    KNOWLEDGE_OVERLAP_SIZE: int = Field(default=200, description="分块重叠大小")
    
    model_config = ConfigDict(
        env_prefix="AI_"  # 使用AI_前缀区分配置
    )
    
    @property
    def llm_config(self) -> Dict:
        """获取LLM配置"""
        return {
            "model": self.LLM_MODEL,
            "temperature": self.LLM_TEMPERATURE,
            "max_tokens": self.LLM_MAX_TOKENS,
            "top_p": self.LLM_TOP_P,
            "frequency_penalty": self.LLM_FREQUENCY_PENALTY,
            "presence_penalty": self.LLM_PRESENCE_PENALTY,
            "stop": self.LLM_STOP_WORDS
        }
    
    @property
    def vector_db_config(self) -> Dict:
        """获取向量数据库配置"""
        return {
            "host": self.VECTOR_DB_HOST,
            "port": self.VECTOR_DB_PORT,
            "user": self.VECTOR_DB_USER,
            "password": self.VECTOR_DB_PASSWORD,
            "collection_name": self.VECTOR_DB_COLLECTION,
            "dimension": self.VECTOR_DIMENSION,
            "metric_type": self.VECTOR_METRIC_TYPE,
            "index_type": self.VECTOR_INDEX_TYPE,
            "nlist": self.VECTOR_NLIST
        }
    
    def _configure_for_environment(self) -> None:
        """根据环境配置特定的设置"""
        super()._configure_for_environment()
        
        if self.ENV == "test":
            # 测试环境使用较小的配置
            self.LLM_MAX_TOKENS = 512
            self.LLM_BATCH_SIZE = 2
            self.VECTOR_NLIST = 128
            self.AI_SERVICE_CONCURRENT_REQUESTS = 2
            self.AI_SERVICE_RATE_LIMIT = 10
        elif self.ENV == "production":
            # 生产环境使用更严格的配置
            self.LLM_TIMEOUT = 60
            self.LLM_RETRY_COUNT = 5
            self.AI_SERVICE_MAX_RETRIES = 5
            self.KNOWLEDGE_CHUNK_SIZE = 500
            self.KNOWLEDGE_OVERLAP_SIZE = 100

# 创建全局AI配置实例
ai_settings = AISettings() 