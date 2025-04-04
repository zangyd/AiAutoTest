import os
import sys
from datetime import datetime
from pathlib import Path

import redis
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class RedisMigration:
    def __init__(self):
        self.client = None
        self.migrations_dir = Path(__file__).parent / 'migrations'
        self.migrations_key = 'schema_migrations'
        
    def connect(self):
        """连接数据库"""
        try:
            self.client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                db=int(os.getenv('REDIS_DB', 0)),
                password=os.getenv('REDIS_PASSWORD', None),
                decode_responses=True
            )
            # 测试连接
            self.client.ping()
        except Exception as e:
            print(f"Redis连接失败: {e}")
            sys.exit(1)

    def get_executed_migrations(self):
        """获取已执行的迁移记录"""
        return set(self.client.hkeys(self.migrations_key))

    def create_migration(self, name):
        """创建新的迁移文件"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"{timestamp}_{name}.py"
        
        # 确保migrations目录存在
        self.migrations_dir.mkdir(parents=True, exist_ok=True)
        
        template = f'''"""
Migration: {name}
Created at: {datetime.now().isoformat()}
"""
import redis

def upgrade(client):
    """执行迁移"""
    # 在此处添加迁移代码
    # 例如：
    # client.set('key', 'value')
    # client.hset('hash', 'field', 'value')
    pass

def downgrade(client):
    """回滚迁移"""
    # 在此处添加回滚代码
    # 例如：
    # client.delete('key')
    # client.hdel('hash', 'field')
    pass
'''
        
        filepath = self.migrations_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(template)
        
        print(f"已创建迁移文件: {filename}")

    def run_migration(self, filename):
        """执行迁移文件"""
        version = filename.split('_')[0]
        name = '_'.join(filename.split('_')[1:]).replace('.py', '')
        
        # 导入迁移模块
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            f"migration_{version}",
            self.migrations_dir / filename
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        try:
            # 执行迁移
            module.upgrade(self.client)
            
            # 记录迁移
            self.client.hset(self.migrations_key, version, name)
            
            print(f"成功执行迁移: {filename}")
        except Exception as e:
            print(f"执行迁移失败 {filename}: {e}")
            try:
                # 尝试回滚
                module.downgrade(self.client)
                print(f"已回滚迁移: {filename}")
            except Exception as rollback_error:
                print(f"回滚失败: {rollback_error}")
            sys.exit(1)

    def migrate(self):
        """执行所有未执行的迁移"""
        self.connect()
        
        # 获取已执行的迁移
        executed = self.get_executed_migrations()
        
        # 获取所有迁移文件
        migration_files = sorted([f.name for f in self.migrations_dir.glob('*.py')
                                if f.name != '__init__.py'])
        
        # 执行未执行的迁移
        for filename in migration_files:
            version = filename.split('_')[0]
            if version not in executed:
                self.run_migration(filename)

    def close(self):
        """关闭数据库连接"""
        if self.client:
            self.client.close()

def main():
    """主函数"""
    migration = RedisMigration()
    
    if len(sys.argv) < 2:
        print("请指定操作: create <name> 或 migrate")
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        if command == 'create':
            if len(sys.argv) < 3:
                print("请指定迁移名称")
                sys.exit(1)
            migration.create_migration(sys.argv[2])
        
        elif command == 'migrate':
            migration.migrate()
        
        else:
            print("未知命令。支持的命令: create <name> 或 migrate")
            sys.exit(1)
    
    finally:
        migration.close()

if __name__ == '__main__':
    main() 