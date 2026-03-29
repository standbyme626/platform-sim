# CHANGELOG

本文件记录对仓库产生持久影响的改动。

---

## 格式
- 日期
- Milestone
- 变更摘要
- 影响范围
- 相关测试
- 相关提交
- 是否已推送远端

---

## 记录示例
### 2026-03-29
- **Milestone**: M1
- **变更摘要**:
  - 新增 apps/official-sim-server 基础骨架
  - 新增 healthz 路由
  - 新增 run create stub
  - 新增 requirements.txt 和 pyproject.toml
  - 新增 pytest markers 配置
- **影响范围**:
  - apps/official-sim-server/app/main.py
  - apps/official-sim-server/app/api/router.py
  - apps/official-sim-server/app/api/routes/runs.py
  - apps/official-sim-server/requirements.txt
  - apps/official-sim-server/pyproject.toml
- **相关测试**: 待补充 (M1 无测试)
- **相关提交**: d42bc0c
- **是否已推送远端**: yes
