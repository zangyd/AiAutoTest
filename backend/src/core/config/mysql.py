import os

class MySQLSettings:
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'Autotest@2024')
    DB_NAME = os.getenv('DB_NAME', 'autotest')
    MYSQL_POOL_SIZE = int(os.getenv('MYSQL_POOL_SIZE', 20))
    MYSQL_POOL_RECYCLE = int(os.getenv('MYSQL_POOL_RECYCLE', 3600))

mysql_settings = MySQLSettings()
