# ExpensePilot · 财务报销 Agent

[Gitee 仓库](https://gitee.com/ouyangzhi66/expensepilot) · [Issues](https://gitee.com/ouyangzhi66/expensepilot/issues) · [评测报告](docs/eval.md) · [开发日志](docs/log.md)

> 员工一句话描述出差 / 招待费用，Agent 查制度、算额度、验发票、生成凭证草稿；超规则自动转人工。

[Demo](TODO) · [3 分钟视频](TODO)

## 为什么不是又一个 RAG 聊天框

报销是一个多步任务：查制度 → 查额度 → 校验发票 → 生成凭证 → 人工确认。单轮 RAG 只能回答“住宿上限多少”，不能完成任务。这个项目要证明的是：

- 多工具编排（7 个工具）
- 多轮槽位填充与追问
- 条件分支与人在回路（超限 / 越权转人工）
- 可评测（30 条场景 + 指标）
- 可观测（审计日志 / trace）

## 架构

```text
员工
  │
  ▼
Streamlit UI ──► LangGraph ──► policy_search ──► Postgres + pgvector
                    │
                    ├──► budget_check ──► Postgres
                    ├──► voucher_create ──► Postgres
                    └──► ask_human ──► 待办 / 审计日志
```

## 快速开始

### 0. 克隆

```powershell
git clone https://gitee.com/ouyangzhi66/expensepilot.git
cd expensepilot
```

### 1. 安装 Python 3.11
安装时勾选 `Add python.exe to PATH`。

### 2. 装依赖

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt
Copy-Item .env.example .env
```

### 3. 数据库（二选一）

- **A. Supabase（推荐，免 Docker）**：新建项目 → SQL Editor 执行 `create extension if not exists vector;` → 把 Session Pooler 连接串填到 `.env` 的 `DATABASE_URL`。
- **B. 本地 Docker**：`docker compose up -d db`。

验证连接：

```powershell
python scripts/db_check.py
```

看到 PostgreSQL 版本和 `pgvector: True` 即成功。

### 4. 初始化表和数据

在 Supabase SQL Editor 依次执行：

1. `db/schema.sql`
2. `db/seed.sql`（会清空这 4 张表，仅用于演示数据）

### 5. 自检

```powershell
.\scripts\check.ps1
```

### 6. 分支与远程

- 主分支：`master`（Gitee 默认）
- 远程：`origin` → `https://gitee.com/ouyangzhi66/expensepilot.git`

> Gitee 不跑 GitHub Actions。`.github/workflows/ci.yml` 只在以后镜像到 GitHub 时用；日常用 `scripts/check.ps1`，Gitee Go 可选，不影响交付。

## 制度 RAG（D02）

```powershell
# 1. 在 Supabase SQL Editor 执行 db/migrations/002_policy_chunks.sql
# 2. 把制度条款切分、向量化、入库
python scripts/ingest_policies.py
# 3. 检索
python scripts/search_policy.py "上海住宿 800 能报吗"
```

默认用本地 `BAAI/bge-small-zh-v1.5`（512 维，约 100MB），不用 API key。首次运行会下载模型；国内网络慢时先设 `$env:HF_ENDPOINT="https://hf-mirror.com"`。

## Agent（D03）

```powershell
python scripts/ask.py "上海住宿800能报吗"
```

Agent 先调用 `policy_search` 查条款，再基于条款回答；回答里真正引用的 `POL-xxx` 会记进 `citations`。

## 预算查询（D04）

```powershell
python scripts/ask.py "李四再报5000住宿呢"
```

Agent 会同时调用 `policy_search` 和 `budget_check`，把制度上限和部门余额分开回答。

## 凭证草稿（D05）

```powershell
python scripts/ask.py "帮张三生成一张上海住宿800元的凭证草稿，2026-10-12到2026-10-13，引用POL-001"
```

`voucher_create` 生成 8 个必填字段，并用 `schemas/voucher.schema.json` 校验；只返回 JSON 草稿，不写库，最终需人工确认。

## 多轮槽位（D06）

```powershell
python scripts/chat.py
```

信息不全时先追问；槽位齐了才查制度/预算/生成凭证。`ask.py` 适合单轮，`chat.py` 用于多轮。

## 网页界面（D07）

```powershell
streamlit run app.py
```

打开 http://localhost:8501 。左侧显示槽位、引用、本轮工具调用和凭证草稿，右侧聊天。

## 评测

| 指标 | 目标 | 当前 |
|---|---|---|
| 任务完成率 | ≥85% | TODO |
| 凭证字段完整率 | ≥95% | 8/8（D05） |
| 超限 / 越权拦截率 | 100% | TODO |
| RAG 引用命中率 | ≥90% | 7/7（D02） |
| P95 时延 | ≤3s | TODO |

场景分布与用例见 [docs/eval.md](docs/eval.md)、[eval/cases.csv](eval/cases.csv)。

## Roadmap

### MVP（10 天）

- [x] D01 数据表 / 合成数据 / 10 条评测集
- [x] D02 制度 RAG：切分、embedding、pgvector、引用
- [x] D03 LangGraph 骨架 + `policy_search`
- [x] D04 `budget_check` + seed SQL
- [x] D05 `voucher_create` + JSON Schema
- [x] D06 多轮槽位 + 缺信息追问
- [x] D07 Streamlit happy path
- [ ] D08 人在回路 + 审计日志
- [ ] D09 15 条评测 + top-3 修复
- [ ] D10 部署 / README / 3 分钟视频

### 加固（D11-D21）

- [ ] 发票 OCR + 票面校验
- [ ] 30 条评测 + 错误分类
- [ ] Langfuse trace / 成本统计
- [ ] Vue 3 前端（可选）
- [ ] 1 页项目报告（Gitee Pages 或 `docs/report.md`）
- [ ] Dockerfile / compose 一键起（面试讲容器化）

## 每日 Gitee 流程

1. 开工：把当天 issue 打开，写一句“今日目标”。
2. 开发：每 30-45 分钟 commit 一次，Conventional Commits。
3. 收工：更新 `docs/log.md`，关闭 issue，README 进度打勾。
4. 每天 push 到 `master`；每周日打 tag（`v0.1.0`），写 Release notes。

10 个 issue 的标题和正文见 [docs/issues.md](docs/issues.md)。

> 贡献度统计要求 `git config user.email` 与 Gitee 绑定邮箱一致。当前本机是 `1161655868@qq.com`，去 Gitee「设置 → 邮箱管理」确认已绑定，否则提交不会变绿。

## 仓库结构

```text
expensepilot/
├─ app.py                 # Streamlit 页面
├─ src/expensepilot/      # Agent / tools / api
├─ db/                    # schema.sql / seed.sql / migrations
├─ schemas/               # voucher.schema.json
├─ eval/                  # 测试集与评测脚本
├─ docs/                  # 日志、评测、ADR
├─ scripts/               # check.ps1 本地自检
├─ tests/                 # pytest
├─ .github/               # GitHub 镜像用 CI + issue 模板
└─ docker-compose.yml     # Postgres + pgvector（可选）
```

## 数据与隐私

- 仓库只含合成数据：姓名、发票号、金额均为虚构。
- 不提交真实姓名、手机号、身份证、银行卡、工资、真实发票、API key、数据库连接串。
- `.env` 已忽略；截图前把姓名、金额、key 打码。
- Supabase 本身可以存真实财务数据（配合 RLS、权限、备份），但本项目演示仍用合成数据，避免误传。

## License

MIT
