import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy import create_engine
from redis.asyncio import Redis
from src.core.config.mongodb import mongodb_settings
from src.core.config.mysql import mysql_settings
from src.core.config.redis import redis_settings

async def init_mongodb():
    """初始化MongoDB连接"""
    client = AsyncIOMotorClient(mongodb_settings.MONGODB_URL,
                              minPoolSize=mongodb_settings.MONGODB_MIN_POOL_SIZE,
                              maxPoolSize=mongodb_settings.MONGODB_MAX_POOL_SIZE,
                              serverSelectionTimeoutMS=mongodb_settings.MONGODB_TIMEOUT_MS)
    db = client[mongodb_settings.MONGODB_DB_NAME]
    try:
        await client.admin.command('ping')
        print("MongoDB连接成功")
        return db
    except Exception as e:
        print(f"MongoDB连接失败: {e}")
        return None

def init_mysql():
    """初始化MySQL连接"""
    try:
        url = f"mysql+pymysql://{mysql_settings.MYSQL_USER}:{mysql_settings.MYSQL_PASSWORD}@{mysql_settings.MYSQL_HOST}:{mysql_settings.MYSQL_PORT}/{mysql_settings.MYSQL_DATABASE}"
        engine = create_engine(url,
                             pool_size=mysql_settings.MYSQL_POOL_SIZE,
                             pool_recycle=mysql_settings.MYSQL_POOL_RECYCLE,
                             pool_pre_ping=True)
        engine.connect()
        print("MySQL连接成功")
        return engine
    except Exception as e:
        print(f"MySQL连接失败: {e}")
        return None

async def init_redis():
    """初始化Redis连接"""
    try:
        redis = Redis(host=redis_settings.REDIS_HOST,
                     port=redis_settings.REDIS_PORT,
                     db=redis_settings.REDIS_DB,
                     password=redis_settings.REDIS_PASSWORD,
                     encoding=redis_settings.REDIS_ENCODING,
                     decode_responses=True)
        await redis.ping()
        print("Redis连接成功")
        return redis
    except Exception as e:
        print(f"Redis连接失败: {e}")
        return None

async def init_all():
    """初始化所有数据库连接"""
    mongodb = await init_mongodb()
    mysql = init_mysql()
    redis = await init_redis()
    return mongodb, mysql, redis

if __name__ == "__main__":
    asyncio.run(init_all()) 