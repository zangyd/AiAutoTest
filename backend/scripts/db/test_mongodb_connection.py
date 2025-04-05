import os
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_mongodb_connection():
    """
    测试MongoDB连接和基本操作
    使用环境变量中的配置进行连接
    """
    try:
        # 从环境变量获取配置
        host = os.getenv('MONGODB_HOST', 'localhost')
        port = int(os.getenv('MONGODB_PORT', 27017))
        username = os.getenv('MONGODB_USER')
        password = os.getenv('MONGODB_PASSWORD')
        database = os.getenv('MONGODB_DATABASE')
        auth_source = os.getenv('MONGODB_AUTH_SOURCE', 'admin')

        # 构建连接URI
        if username and password:
            uri = f"mongodb://{username}:{password}@{host}:{port}/{database}?authSource={auth_source}"
        else:
            uri = f"mongodb://{host}:{port}/{database}"

        # 创建MongoDB客户端
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)

        # 验证连接
        client.admin.command('ping')
        logger.info("MongoDB连接成功!")

        # 获取数据库
        db = client[database]
        
        # 测试集合操作
        collection = db['test_collection']
        
        # 插入测试文档
        test_doc = {"test_key": "test_value", "status": "testing"}
        insert_result = collection.insert_one(test_doc)
        logger.info(f"插入测试文档成功，ID: {insert_result.inserted_id}")
        
        # 查询测试文档
        found_doc = collection.find_one({"test_key": "test_value"})
        logger.info(f"查询测试文档成功: {found_doc}")
        
        # 更新测试文档
        update_result = collection.update_one(
            {"test_key": "test_value"},
            {"$set": {"status": "tested"}}
        )
        logger.info(f"更新测试文档成功，匹配数: {update_result.matched_count}")
        
        # 删除测试文档
        delete_result = collection.delete_one({"test_key": "test_value"})
        logger.info(f"删除测试文档成功，删除数: {delete_result.deleted_count}")
        
        # 删除测试集合
        collection.drop()
        logger.info("测试集合清理完成")
        
        return True

    except ConnectionFailure as e:
        logger.error(f"MongoDB连接失败: {str(e)}")
        return False
    except OperationFailure as e:
        logger.error(f"MongoDB操作失败: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"MongoDB测试过程出现异常: {str(e)}")
        return False
    finally:
        if 'client' in locals():
            client.close()
            logger.info("MongoDB连接已关闭")

if __name__ == "__main__":
    test_mongodb_connection() 