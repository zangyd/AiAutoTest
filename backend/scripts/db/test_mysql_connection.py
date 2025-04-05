import os
import logging
import mysql.connector
from mysql.connector import Error

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_mysql_connection():
    """
    测试MySQL连接和基本操作
    使用环境变量中的配置进行连接
    """
    connection = None
    try:
        # 从环境变量获取配置
        host = os.getenv('DB_HOST', 'localhost')
        port = int(os.getenv('DB_PORT', 3306))
        user = os.getenv('DB_USER', 'root')
        password = os.getenv('DB_PASSWORD')
        database = os.getenv('DB_NAME')

        # 创建数据库连接
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )

        if connection.is_connected():
            db_info = connection.get_server_info()
            logger.info(f"MySQL连接成功! 服务器版本: {db_info}")

            # 创建游标
            cursor = connection.cursor()

            # 创建测试表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_table (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    status VARCHAR(50)
                )
            """)
            logger.info("测试表创建成功")

            # 插入测试数据
            sql_insert = "INSERT INTO test_table (name, status) VALUES (%s, %s)"
            test_data = ("test_item", "testing")
            cursor.execute(sql_insert, test_data)
            connection.commit()
            logger.info(f"插入测试数据成功，ID: {cursor.lastrowid}")

            # 查询测试数据
            cursor.execute("SELECT * FROM test_table WHERE name = 'test_item'")
            result = cursor.fetchone()
            logger.info(f"查询测试数据成功: {result}")

            # 更新测试数据
            sql_update = "UPDATE test_table SET status = %s WHERE name = %s"
            cursor.execute(sql_update, ("tested", "test_item"))
            connection.commit()
            logger.info(f"更新测试数据成功，影响行数: {cursor.rowcount}")

            # 删除测试数据
            cursor.execute("DELETE FROM test_table WHERE name = 'test_item'")
            connection.commit()
            logger.info(f"删除测试数据成功，影响行数: {cursor.rowcount}")

            # 删除测试表
            cursor.execute("DROP TABLE test_table")
            logger.info("测试表删除成功")

            cursor.close()
            return True

    except Error as e:
        logger.error(f"MySQL连接错误: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"MySQL测试过程出现异常: {str(e)}")
        return False
    finally:
        if connection and connection.is_connected():
            connection.close()
            logger.info("MySQL连接已关闭")

if __name__ == "__main__":
    test_mysql_connection() 