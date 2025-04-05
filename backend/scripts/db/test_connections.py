import sys
import os
import asyncio
from sqlalchemy import create_engine, text
from pymongo import MongoClient
import redis
from loguru import logger
from urllib.parse import quote_plus

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.core.config.mysql import mysql_settings
from src.core.config.mongodb import mongodb_settings
from src.core.config.redis import redis_settings

logger.add("connection_test.log", rotation="500 MB")

async def test_mysql_connection():
    try:
        # 构建MySQL连接URL，对密码进行URL编码
        mysql_url = f"mysql+pymysql://{mysql_settings.DB_USER}:{quote_plus(mysql_settings.DB_PASSWORD)}@{mysql_settings.DB_HOST}:{mysql_settings.DB_PORT}/{mysql_settings.DB_NAME}"
        engine = create_engine(mysql_url)
        
        # 测试连接
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            logger.success("MySQL连接测试成功！")
            return True
    except Exception as e:
        logger.error(f"MySQL连接测试失败: {str(e)}")
        return False

async def test_mongodb_connection():
    try:
        # 创建MongoDB客户端
        client = MongoClient(mongodb_settings.MONGODB_URL,
                           minPoolSize=mongodb_settings.MONGODB_MIN_POOL_SIZE,
                           maxPoolSize=mongodb_settings.MONGODB_MAX_POOL_SIZE,
                           serverSelectionTimeoutMS=mongodb_settings.MONGODB_TIMEOUT_MS)
        
        # 测试连接
        client.admin.command('ping')
        logger.success("MongoDB连接测试成功！")
        client.close()
        return True
    except Exception as e:
        logger.error(f"MongoDB连接测试失败: {str(e)}")
        return False

async def test_redis_connection():
    try:
        # 创建Redis客户端
        redis_client = redis.Redis(
            host=redis_settings.REDIS_HOST,
            port=redis_settings.REDIS_PORT,
            db=redis_settings.REDIS_DB,
            password=redis_settings.REDIS_PASSWORD,
            encoding=redis_settings.REDIS_ENCODING,
            decode_responses=True
        )
        
        # 测试连接
        redis_client.ping()
        logger.success("Redis连接测试成功！")
        redis_client.close()
        return True
    except Exception as e:
        logger.error(f"Redis连接测试失败: {str(e)}")
        return False

async def main():
    logger.info("开始测试数据库连接...")
    
    # 测试所有数据库连接
    mysql_result = await test_mysql_connection()
    mongodb_result = await test_mongodb_connection()
    redis_result = await test_redis_connection()
    
    # 输出总结
    logger.info("\n连接测试结果总结:")
    logger.info(f"MySQL: {'✓' if mysql_result else '✗'}")
    logger.info(f"MongoDB: {'✓' if mongodb_result else '✗'}")
    logger.info(f"Redis: {'✓' if redis_result else '✗'}")
    
    # 如果有任何连接失败，返回非零状态码
    if not all([mysql_result, mongodb_result, redis_result]):
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 