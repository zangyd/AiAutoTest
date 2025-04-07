"""测试运行脚本"""
import sys
import os
from pathlib import Path
import argparse
import pytest

# 添加项目根目录到Python路径
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

# 设置测试环境变量
os.environ["ENV"] = "test"
os.environ["TESTING"] = "True"
os.environ["JWT_SECRET_KEY"] = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
os.environ["JWT_ALGORITHM"] = "HS256"

def main():
    """运行测试"""
    parser = argparse.ArgumentParser(description="运行测试")
    parser.add_argument("test_path", help="要运行的测试路径", nargs="?", default="src/tests")
    parser.add_argument("-v", "--verbose", help="显示详细输出", action="store_true")
    args = parser.parse_args()
    
    test_args = [args.test_path]
    if args.verbose:
        test_args.append("-v")
    
    print(f"运行测试: {' '.join(test_args)}")
    print(f"PYTHONPATH: {sys.path}")
    
    return pytest.main(test_args)

if __name__ == "__main__":
    sys.exit(main()) 