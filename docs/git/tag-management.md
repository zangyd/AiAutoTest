# Git标签管理规范

## 版本标签规范
- 格式：v{major}.{minor}.{patch}
  - major：主版本号，重大功能变更
  - minor：次版本号，新功能发布
  - patch：修订号，bug修复和小改动
- 示例：v1.0.0, v1.1.0, v1.1.1

## 环境标签规范
- 格式：{env}-{timestamp}
  - env：环境标识（prod/test/dev）
  - timestamp：时间戳（YYYYMMDD）
- 示例：prod-20240401, test-20240401, dev-20240401

## 里程碑标签规范
- 格式：milestone-{name}-{date}
  - name：里程碑名称
  - date：日期（YYYYMMDD）
- 示例：milestone-beta-20240401

## 标签创建流程
1. 确认代码已经完成review并合并到目标分支
2. 在目标分支上创建标签
3. 添加标签说明信息
4. 推送标签到远程仓库

## 标签管理命令
```bash
# 创建标签
git tag -a v1.0.0 -m "version 1.0.0 release"

# 推送标签
git push origin v1.0.0

# 查看标签
git tag -l

# 删除标签
git tag -d v1.0.0
git push origin :v1.0.0
``` 