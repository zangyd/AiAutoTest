import os
import logging
import redis
from redis.exceptions import ConnectionError, RedisError

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_redis_connection():
    """
    测试Redis连接和基本操作
    使用环境变量中的配置进行连接
    """
    try:
        # 从环境变量获取配置
        host = os.getenv('REDIS_HOST', 'localhost')
        port = int(os.getenv('REDIS_PORT', 6379))
        password = os.getenv('REDIS_PASSWORD')
        db = int(os.getenv('REDIS_DB', 0))

        # 创建Redis客户端
        client = redis.Redis(
            host=host,
            port=port,
            password=password,
            db=db,
            socket_timeout=5,
            decode_responses=True
        )

        # 测试连接
        client.ping()
        logger.info("Redis连接成功!")

        # 测试字符串操作
        test_key = "test:string"
        client.set(test_key, "test_value")
        value = client.get(test_key)
        logger.info(f"字符串操作测试成功: {value}")

        # 测试列表操作
        list_key = "test:list"
        client.rpush(list_key, "item1", "item2", "item3")
        list_items = client.lrange(list_key, 0, -1)
        logger.info(f"列表操作测试成功: {list_items}")

        # 测试集合操作
        set_key = "test:set"
        client.sadd(set_key, "member1", "member2", "member3")
        set_members = client.smembers(set_key)
        logger.info(f"集合操作测试成功: {set_members}")

        # 测试哈希操作
        hash_key = "test:hash"
        client.hset(hash_key, mapping={"field1": "value1", "field2": "value2"})
        hash_values = client.hgetall(hash_key)
        logger.info(f"哈希操作测试成功: {hash_values}")

        # 清理测试数据
        client.delete(test_key, list_key, set_key, hash_key)
        logger.info("测试数据清理完成")

        return True

    except ConnectionError as e:
        logger.error(f"Redis连接错误: {str(e)}")
        return False
    except RedisError as e:
        logger.error(f"Redis操作错误: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Redis测试过程出现异常: {str(e)}")
        return False
    finally:
        if 'client' in locals():
            client.close()
            logger.info("Redis连接已关闭")

if __name__ == "__main__":
    test_redis_connection() 