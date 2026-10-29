# ExpensePilot 项目交接

> 新会话先读这份文件，再继续。最后更新：2026-10-29

## 一句话状态

ExpensePilot 财务报销 Agent 已完成 D01–D10（部署、指标回填、tag v0.1.0），**只剩 3 分钟演示视频**。

## 关键路径与链接

- 项目目录：`D:\deeekseek工作区\expensepilot`
- 线上应用：https://expensepilot-brtprbnrauirgule8zeg8y.streamlit.app（2026-10-29 复验：正常单生成凭证 `V2026...AE78`、异常单转人工 `H2026...0617`，截图在 `docs/screenshots/`）
- Gitee（主仓库）：https://gitee.com/ouyangzhi66/expensepilot
- GitHub（部署镜像）：https://github.com/ouyangzhi66/expensepilot（2026-10-29 已与 Gitee 对齐到同一提交）
- 最新提交：`git log -1`（D10 收尾：指标回填 + 线上复验 + tag）
- 简历新版：`D:\简历\2023-软件工程-欧阳智-Java后端-简历-v2.pdf`
- 简历脚本：`D:\deeekseek工作区\build_resume.py`

## 环境

- Python 3.11.9：`C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe`
- 虚拟环境：`D:\deeekseek工作区\expensepilot\.venv`
- pip 缓存：`D:\deeekseek工作区\.cache\pip`
- embedding 缓存：`expensepilot\.cache\fastembed`
- 数据库：Supabase PostgreSQL + pgvector，Session Pooler（IPv4）
- LLM：DeepSeek `deepseek-chat`，OpenAI 兼容接口
- embedding：`BAAI/bge-small-zh-v1.5`（512 维，本地 fastembed）
- Streamlit Cloud 用 `st.secrets`；本地用 `.env`，`.env` 不提交

## 已完成

| Day | 内容 | 结果 |
|---|---|---|
| D01 | 4 张表 + 合成数据 | 5/15/11/10，pgvector=True |
| D02 | 制度 RAG | 11 条款，top1 7/7 |
| D03 | LangGraph + policy_search | 单轮 Agent 跑通 |
| D04 | budget_check | 余额 7100、超 600 |
| D05 | voucher_create + JSON Schema | 8/8 字段，税额 45.28 |
| D06 | 多轮槽位 | 5 条模糊输入正确追问 |
| D07 | Streamlit UI | AppTest 通过 |
| D08 | 转人工 + 审计 | 工单 pending，audit_logs 留痕 |
| D09 | 15 条端到端评测 | 15/15 通过 |
| D10 | 部署 + README + 视频 | 线上可访问；指标回填（拦截 6/6、P95 21.3s）；tag `v0.1.0`；视频待录 |

## 常用命令

```powershell
cd "D:\deeekseek工作区\expensepilot"
.\.venv\Scripts\Activate.ps1
python scripts\ask.py "住宿标准是多少"
python scripts\chat.py
python scripts\eval_agent.py
.\.venv\Scripts\pytest.exe -q
.\.venv\Scripts\ruff.exe check .
streamlit run app.py
```

## 待办

1. 按 `docs/demo-script.md` 录 3 分钟视频，传 B 站/YouTube。
2. 把视频链接填进 README「演示视频」，D10 打勾，关 D10 issue：
   https://gitee.com/ouyangzhi66/expensepilot/issues/IKQRWQ
3. GitHub 镜像已对齐（`git push github master --force`，`src/` 与本地一致）；下次改动后记得再同步一次。
4. 可选：P95 21.3s 偏慢，先做槽位解析「规则优先 + 小模型兜底」，再谈流式。
5. 可选：出一版只写「Java 后端开发实习生」的简历，AI Agent 只作为项目亮点。

## 已知坑

- **GitHub 从本机/agent 网络访问不稳定**：`git push github` 会超时；网页能打开时用 Upload files。2026-10-29 直连成功过一次，可重试 `git push github master --force`。
- **Streamlit Cloud 曾用 Python 3.14**：应用目前能跑；若重部署报 onnxruntime/fastembed，改成 3.11。
- **Secrets 占位符**：`postgres.xxxx`、`你的密码`、`sk-` 必须换成真实值；已配置成功。
- **GitHub 仓库里有 `db/迁移/`**：不影响运行，规范路径应为 `db/migrations/`。
- **`voucher.py` 启动时读取 `schemas/voucher.schema.json`**：这个文件必须存在。
- **隐私**：仓库只放合成数据；真实姓名、发票、银行卡、API key、连接串不进 Git/截图。
- **时延**：每轮先调一次 LLM 做意图/槽位解析，再跑 agent ↔ tools，P95 21.3s、均值 11.9s；别在面试里说「3 秒内」。

## 会话约定

- 下载/缓存尽量放 D 盘。
- 涉及个人隐私和财产的内容一律不上传。
- 回答用中文，步骤要具体、可执行。
