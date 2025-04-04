import os
import sys
from datetime import datetime
from pathlib import Path

import pymysql
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class MySQLMigration:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.migrations_dir = Path(__file__).parent / 'migrations'
        self.migrations_table = 'schema_migrations'
        
    def connect(self):
        """连接数据库"""
        try:
            self.conn = pymysql.connect(
                host=os.getenv('MYSQL_HOST', 'localhost'),
                port=int(os.getenv('MYSQL_PORT', 3306)),
                user=os.getenv('MYSQL_USER', 'root'),
                password=os.getenv('MYSQL_PASSWORD', ''),
                database=os.getenv('MYSQL_DATABASE', 'autotest'),
                charset='utf8mb4'
            )
            self.cursor = self.conn.cursor()
        except Exception as e:
            print(f"数据库连接失败: {e}")
            sys.exit(1)

    def init_migrations_table(self):
        """初始化迁移记录表"""
        sql = f"""
        CREATE TABLE IF NOT EXISTS {self.migrations_table} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            version VARCHAR(255) NOT NULL,
            name VARCHAR(255) NOT NULL,
            executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            print(f"创建迁移记录表失败: {e}")
            self.conn.rollback()
            sys.exit(1)

    def get_executed_migrations(self):
        """获取已执行的迁移记录"""
        sql = f"SELECT version FROM {self.migrations_table}"
        self.cursor.execute(sql)
        return {row[0] for row in self.cursor.fetchall()}

    def create_migration(self, name):
        """创建新的迁移文件"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"{timestamp}_{name}.sql"
        
        # 确保migrations目录存在
        self.migrations_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = self.migrations_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"-- Migration: {name}\n")
            f.write(f"-- Created at: {datetime.now().isoformat()}\n\n")
            f.write("-- 执行迁移\n")
            f.write("-- 在此处添加您的SQL语句\n\n")
            f.write("-- 回滚迁移\n")
            f.write("-- 在此处添加回滚SQL语句\n")
        
        print(f"已创建迁移文件: {filename}")

    def run_migration(self, filename):
        """执行迁移文件"""
        version = filename.split('_')[0]
        name = '_'.join(filename.split('_')[1:]).replace('.sql', '')
        
        # 读取迁移文件
        with open(self.migrations_dir / filename, 'r', encoding='utf-8') as f:
            sql = f.read()

        try:
            # 执行迁移
            self.cursor.execute(sql)
            
            # 记录迁移
            insert_sql = f"""
            INSERT INTO {self.migrations_table} (version, name)
            VALUES (%s, %s)
            """
            self.cursor.execute(insert_sql, (version, name))
            
            self.conn.commit()
            print(f"成功执行迁移: {filename}")
        except Exception as e:
            print(f"执行迁移失败 {filename}: {e}")
            self.conn.rollback()
            sys.exit(1)

    def migrate(self):
        """执行所有未执行的迁移"""
        self.connect()
        self.init_migrations_table()
        
        # 获取已执行的迁移
        executed = self.get_executed_migrations()
        
        # 获取所有迁移文件
        migration_files = sorted([f.name for f in self.migrations_dir.glob('*.sql')])
        
        # 执行未执行的迁移
        for filename in migration_files:
            version = filename.split('_')[0]
            if version not in executed:
                self.run_migration(filename)

    def close(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

def main():
    """主函数"""
    migration = MySQLMigration()
    
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