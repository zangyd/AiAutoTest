# 认证模块测试说明

本目录包含对认证模块核心功能的测试，特别是验证码和登录日志功能。

## 测试文件说明

### 标准测试文件

这些文件依赖于`conftest.py`中的测试配置，适合在完整的测试环境中运行：

1. **test_captcha.py**: 验证码管理器单元测试
2. **test_login_log.py**: 登录日志服务单元测试
3. **test_token_blacklist.py**: 令牌黑名单单元测试

### 独立测试文件

这些文件不依赖于`conftest.py`，可以在任何环境中独立运行：

1. **standalone_test.py**: 验证码管理器独立测试
2. **standalone_login_log_test.py**: 登录日志服务独立测试
3. **complete_standalone_test.py**: 综合独立测试，包含验证码、登录日志和API集成测试

## 测试范围

### 验证码功能测试

验证码功能测试覆盖以下场景：

1. 生成验证码
   - 检查生成的验证码是否包含必要的字段
   - 验证缓存存储操作

2. 验证码验证
   - 成功验证有效验证码
   - 验证码不区分大小写
   - 验证无效验证码
   - 验证已使用的验证码
   - 验证空输入

### 登录日志功能测试

登录日志功能测试覆盖以下场景：

1. 记录登录情况
   - 记录成功登录
   - 记录失败登录（如验证码错误）
   - 记录登录失败原因

2. 异常处理
   - 处理数据库错误
   - 正确处理缺失字段

### API集成测试

API集成测试模拟完整的登录流程：

1. 生成验证码
2. 用户提交验证码和凭据
3. 验证验证码
4. 验证用户凭据
5. 记录登录行为

## 运行测试

### 运行标准测试

```bash
cd /data/projects/autotest/backend
python -m pytest src/tests/core/auth/test_captcha.py -v
python -m pytest src/tests/core/auth/test_login_log.py -v
```

### 运行独立测试

```bash
cd /data/projects/autotest/backend/src
python tests/core/auth/standalone_test.py
python tests/core/auth/standalone_login_log_test.py
python tests/core/auth/complete_standalone_test.py
```

## 测试结果

完整的独立测试显示所有验证码和登录日志功能都正常工作。测试涵盖了核心功能和边缘情况，确保功能在各种情况下表现稳定。

```
=== 测试验证码管理器 ===
测试生成验证码...
✓ 验证码生成测试通过
测试验证码验证成功...
✓ 验证码验证成功测试通过
测试验证码不区分大小写...
✓ 验证码不区分大小写测试通过
测试验证码验证失败 - 错误的验证码...
✓ 验证码验证失败测试通过
测试验证码验证失败 - 已使用的验证码...
✓ 已使用的验证码测试通过
测试验证码验证失败 - 空输入...
✓ 空输入测试通过

=== 测试登录日志服务 ===
测试记录成功登录...
✓ 记录成功登录测试通过
测试记录失败登录...
✓ 记录失败登录测试通过
测试记录登录异常处理...
✓ 记录登录异常处理测试通过

=== 测试认证API集成 ===
测试登录流程...
✓ 登录流程测试通过
测试登录失败 - 验证码错误...
✓ 登录失败 - 验证码错误测试通过

✓✓✓ 所有测试通过! ✓✓✓ 