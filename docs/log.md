# 开发日志

> 收工前 3 行；commit：`chore(log): Dxx`

| 日期 | Day | 今日目标 | 完成 | 卡点 | 明日 | Commit |
|---|---|---|---|---|---|---|
| 2026-10-27 | D00 | 建仓库 / CI / 10 个 issue | 仓库可 push，CI 绿 | - | D01 数据与评测集 | `8a38cee` |
| 2026-10-27 | D01 | 数据表 / 合成数据 / 10 条评测集 | schema、seed、cases 已提交；Supabase 验证 5/15/11/10，pgvector=True | - | D02 制度 RAG | `35e5b8e` |
| 2026-10-28 | D02 | 制度 RAG：切分、embedding、pgvector、引用 | 11 条制度入 policy_chunks；7 条问题 top1 7/7、top3 7/7 | 模型缓存放 `.cache`，避开 C 盘写入限制 | D03 LangGraph | `9f8fdfa` |
| 2026-10-29 | D03 | LangGraph 骨架 + policy_search | agent↔tools 跑通；引用、拒答、闲聊三条验收通过 | - | D04 budget_check | `16d6d53` |
