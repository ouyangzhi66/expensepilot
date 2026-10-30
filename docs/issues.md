# 10 个 issue（复制到 Gitee）

## 怎么建

1. 打开仓库 → **Issues** → **新建 Issue**。
2. 标题、正文从下面复制。
3. 右侧「标签」选 `day`；没有这个标签就先点「标签 → 新建标签」，名称 `day`，颜色随便选。
4. 点「创建」。

标签不是必须的：不想建标签，就在标题前保留 `D01`、`D02`，一样能筛。Gitee 个人仓库没有 GitHub Projects 那种看板，**打开 = 进行中，关闭 = 完成**，两态就够。

## D01 数据表 + 合成数据 + 10 条评测集

目标：把报销业务的数据模型和第一批测试场景定下来。

- [ ] 4 张表：employees、budgets、policies、reimbursements
- [ ] 20 条合成数据（不要用真实姓名 / 手机号 / 发票）
- [ ] `eval/cases.csv` 10 条，覆盖正常 / 超限 / 缺票 / 模糊 / 越权

产出：`db/schema.sql`、`db/seed.sql`、`eval/cases.csv`
Commit：`feat(db): add schema and synthetic seed data`

## D02 制度 RAG

目标：制度文档入库，能按问题召回条款。

- [ ] 按条款切分（不要按固定字数硬切）
- [ ] embedding + pgvector 入库
- [ ] top-k 返回条款号 + 原文
- [ ] 5 个制度问题，至少 4 个命中正确条款

产出：`src/expensepilot/rag.py`、`scripts/ingest_policies.py`
Commit：`feat(rag): ingest policies with clause-level chunks`

## D03 LangGraph 骨架 + policy_search

目标：跑通「输入 → Agent → 工具 → 回答」。

- [ ] StateGraph：agent → tools → agent
- [ ] state 含 messages、slots、citations
- [ ] 单轮「广州住宿上限多少」能答且带引用

产出：`graph.py`、`state.py`、`tools/policy.py`
Commit：`feat(agent): add policy_search tool with citations`

## D04 budget_check

目标：能查额度、判断超标。

- [ ] `budget_check(employee_id, city, category)` 返回额度 / 已用 / 剩余
- [ ] 住宿、餐补、交通三类超标判断
- [ ] 3 个查询结果正确

产出：`tools/budget.py`、`db/seed.sql`
Commit：`feat(agent): add budget_check`

## D05 voucher_create

目标：生成合法凭证草稿。

- [ ] 8 个字段：报销人 / 部门 / 费用类型 / 金额 / 税额 / 摘要 / 科目 / 条款引用
- [ ] JSON Schema 校验
- [ ] 金额与明细加总一致

产出：`tools/voucher.py`、`schemas/voucher.json`
Commit：`feat(agent): create validated voucher draft`

## D06 多轮槽位

目标：缺信息会追问，而不是硬编。

- [ ] 缺城市 / 天数 / 费用类型时追问
- [ ] 5 条模糊输入都能问回缺失项
- [ ] 槽位齐了再生成凭证

产出：`graph.py` 槽位节点
Commit：`feat(agent): slot filling and clarification`

## D07 Streamlit happy path

目标：本地能演示完整一条正常报销。

- [ ] 输入一句话 → 展示工具调用 → 凭证草稿
- [ ] 展示引用条款
- [ ] `streamlit run` 可跑

产出：`app.py`
Commit：`feat(ui): streamlit happy path`
Tag：`v0.0.1`

## D08 人在回路 + 审计日志

目标：超限 / 越权会转人工，并留下记录。

- [ ] 超限 / 越权 → `ask_human`，返回待办
- [ ] 审计日志：时间 / 输入 / 工具 / 结果 / 是否转人工
- [ ] 人工确认后继续

产出：`tools/human.py`、`audit.py`
Commit：`feat(agent): human approval and audit log`

## D09 15 条评测

目标：用数据说明它到底行不行。

- [ ] 15 条 cases 跑通
- [ ] 指标：完成率 / 字段完整率 / 拦截率 / 引用命中
- [ ] 错误分类 + top3 修复

产出：`scripts/eval_agent.py`、更新 `docs/eval.md`
Commit：`test(eval): add 15-case harness`

## D10 部署 + 文档

目标：公网能点开，别人能照着跑通。

- [ ] Streamlit Cloud 公网可访问
- [ ] README 有架构 / 评测 / quickstart
- [ ] 3 分钟视频
- [ ] tag `v0.1.0`

产出：公网链接 + 视频
Commit：`docs: add demo and architecture`
