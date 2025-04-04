"""
Migration: init_cache_config
Created at: 2024-04-03T00:00:01
"""
import redis

def upgrade(client):
    """执行迁移"""
    # 设置缓存配置
    cache_config = {
        'user_cache_ttl': 3600,  # 用户信息缓存时间（秒）
        'project_cache_ttl': 7200,  # 项目信息缓存时间（秒）
        'test_case_cache_ttl': 1800,  # 测试用例缓存时间（秒）
        'api_rate_limit': 100,  # API速率限制（次/分钟）
        'max_failed_login_attempts': 5,  # 最大登录失败次数
        'login_block_duration': 900,  # 登录锁定时间（秒）
    }
    
    # 使用hash存储所有配置
    client.hmset('system:cache_config', cache_config)
    
    # 设置一些默认的键过期时间
    client.config_set('maxmemory-policy', 'allkeys-lru')
    
    # 设置常用计数器
    client.set('counters:total_users', 0)
    client.set('counters:total_projects', 0)
    client.set('counters:total_test_cases', 0)
    
    # 设置在线用户集合
    client.delete('online_users')
    client.sadd('online_users', 'system')  # 添加系统用户作为默认值

def downgrade(client):
    """回滚迁移"""
    # 删除所有配置
    client.delete('system:cache_config')
    
    # 删除计数器
    client.delete('counters:total_users')
    client.delete('counters:total_projects')
    client.delete('counters:total_test_cases')
    
    # 删除在线用户集合
    client.delete('online_users') 