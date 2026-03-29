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

---

### 2026-03-29
- **Milestone**: M2
- **变更摘要**:
  - 新增 Alembic 配置和迁移
  - 新增 6 张核心表（simulation_runs, simulation_events, state_snapshots, push_events, artifacts, evaluation_reports）
  - 新增 repository skeleton（run_repo, event_repo, snapshot_repo）
  - 新增 SQLite 本地数据库支持
  - 更新 runs.py 实际连接 DB
  - 新增 app/core/config.py 和 app/core/database.py
  - 新增 app/models/models.py
- **影响范围**:
  - apps/official-sim-server/alembic/
  - apps/official-sim-server/alembic.ini
  - apps/official-sim-server/app/core/config.py
  - apps/official-sim-server/app/core/database.py
  - apps/official-sim-server/app/models/models.py
  - apps/official-sim-server/app/repositories/run_repo.py
  - apps/official-sim-server/app/repositories/event_repo.py
  - apps/official-sim-server/app/repositories/snapshot_repo.py
  - apps/official-sim-server/app/api/routes/runs.py
  - apps/official-sim-server/requirements.txt
- **相关测试**: 待补充
- **相关提交**: 待推送
- **是否已推送远端**: no
