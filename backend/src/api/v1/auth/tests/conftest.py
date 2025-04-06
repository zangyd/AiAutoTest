"""
测试配置文件
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.src.api.v1.auth.router import router

@pytest.fixture
def app():
    """创建测试应用"""
    app = FastAPI()
    app.include_router(router)
    return app

@pytest.fixture
def client(app):
    """创建测试客户端"""
    return TestClient(app) 