import os

class RedisSettings:
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', 'Autotest@2024')
    REDIS_ENCODING = os.getenv('REDIS_ENCODING', 'utf-8')

redis_settings = RedisSettings()
