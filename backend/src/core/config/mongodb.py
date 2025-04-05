import os
from urllib.parse import quote_plus

class MongoDBSettings:
    MONGODB_HOST = os.getenv('MONGODB_HOST', 'localhost')
    MONGODB_PORT = int(os.getenv('MONGODB_PORT', 27017))
    MONGODB_USER = os.getenv('MONGODB_USER', 'admin')
    MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD', 'Autotest@2024')
    MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'admin')
    MONGODB_AUTH_SOURCE = os.getenv('MONGODB_AUTH_SOURCE', 'admin')
    MONGODB_MIN_POOL_SIZE = int(os.getenv('MONGODB_MIN_POOL_SIZE', 10))
    MONGODB_MAX_POOL_SIZE = int(os.getenv('MONGODB_MAX_POOL_SIZE', 100))
    MONGODB_TIMEOUT_MS = int(os.getenv('MONGODB_TIMEOUT_MS', 5000))

    @property
    def MONGODB_URL(self):
        return f"mongodb://{quote_plus(self.MONGODB_USER)}:{quote_plus(self.MONGODB_PASSWORD)}@{self.MONGODB_HOST}:{self.MONGODB_PORT}/{self.MONGODB_DATABASE}?authSource={self.MONGODB_AUTH_SOURCE}"

mongodb_settings = MongoDBSettings()
