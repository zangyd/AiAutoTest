"""
Migration: create_test_cases_collection
Created at: 2024-04-03T00:00:01
"""
from pymongo import MongoClient, ASCENDING, TEXT

def upgrade(db):
    """执行迁移"""
    # 创建测试用例集合
    if 'test_cases' not in db.list_collection_names():
        db.create_collection('test_cases')
    
    # 创建索引
    db.test_cases.create_index([('title', TEXT)])
    db.test_cases.create_index([('project_id', ASCENDING)])
    db.test_cases.create_index([('status', ASCENDING)])
    db.test_cases.create_index([('created_at', ASCENDING)])
    
    # 创建验证规则
    db.command({
        'collMod': 'test_cases',
        'validator': {
            '$jsonSchema': {
                'bsonType': 'object',
                'required': ['title', 'project_id', 'status', 'created_by'],
                'properties': {
                    'title': {
                        'bsonType': 'string',
                        'description': '测试用例标题'
                    },
                    'description': {
                        'bsonType': 'string',
                        'description': '测试用例描述'
                    },
                    'project_id': {
                        'bsonType': 'objectId',
                        'description': '所属项目ID'
                    },
                    'status': {
                        'enum': ['draft', 'active', 'deprecated'],
                        'description': '测试用例状态'
                    },
                    'type': {
                        'enum': ['functional', 'performance', 'security', 'ui', 'api'],
                        'description': '测试用例类型'
                    },
                    'priority': {
                        'enum': ['P0', 'P1', 'P2', 'P3', 'P4'],
                        'description': '优先级'
                    },
                    'steps': {
                        'bsonType': 'array',
                        'description': '测试步骤'
                    },
                    'expected_results': {
                        'bsonType': 'array',
                        'description': '预期结果'
                    },
                    'tags': {
                        'bsonType': 'array',
                        'description': '标签'
                    },
                    'created_by': {
                        'bsonType': 'objectId',
                        'description': '创建者ID'
                    },
                    'created_at': {
                        'bsonType': 'date',
                        'description': '创建时间'
                    },
                    'updated_at': {
                        'bsonType': 'date',
                        'description': '更新时间'
                    }
                }
            }
        }
    })

def downgrade(db):
    """回滚迁移"""
    # 删除索引
    db.test_cases.drop_indexes()
    
    # 删除集合
    db.test_cases.drop() 