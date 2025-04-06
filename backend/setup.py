from setuptools import setup, find_packages

setup(
    name="autotest-backend",
    version="0.1.0",
    description="自动化测试平台后端服务",
    author="AutoTest Team",
    author_email="autotest@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "fastapi",
        "pyjwt",
        "pytest",
        "pytest-asyncio",
        "pytest-playwright",
        "uvicorn>=0.15.0",
        "sqlalchemy>=1.4.0",
        "pydantic>=1.8.0",
        "python-dotenv>=0.19.0",
        "alembic>=1.7.0",
        "passlib>=1.7.4",
        "python-jose[cryptography]>=3.3.0",
        "bcrypt>=3.2.0",
        "aioredis>=2.0.0",
        "python-multipart>=0.0.5",
        "requests>=2.26.0",
        "pymongo>=3.12.0",
        "motor>=2.5.0",
    ],
    extras_require={
        "dev": [
            "black>=21.7b0",
            "flake8>=3.9.0",
            "isort>=5.9.0",
            "mypy>=0.910",
            "pytest-cov>=2.12.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "autotest-backend=src.main:start",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
) 