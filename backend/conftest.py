"""
测试环境配置
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
ROOT_DIR = Path(__file__).parent
SRC_DIR = ROOT_DIR / "src"
sys.path.append(str(ROOT_DIR))
sys.path.append(str(SRC_DIR))

# 设置测试环境变量
os.environ["TESTING"] = "1"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["JWT_SECRET_KEY"] = "test_secret_key"
os.environ["JWT_ALGORITHM"] = "HS256" 