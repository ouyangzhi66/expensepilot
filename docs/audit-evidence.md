# 人在回路留痕（审计证据）

「超限 / 越权转人工」不是只写在文档里：每次工具调用和每张工单都落到数据库，可以用一条命令核对。

## 复现

```powershell
cd expensepilot
.\.venv\Scripts\Activate.ps1
python scripts\audit_report.py 5
```

## 实际输出（2026-10-30 取数，库内为测试与演示产生的记录）

```text
== 最近 5 条转人工工单 ==
H202610290757570617 | 李四 | 预算超支（市场部2026-10住宿剩余4400元，本次5000元，超出600元）且住宿费超制度上限（POL-001：上海500元/晚，2晚上限1000元，申报5000元，超标4000元需事前审批） | 5000.00 | pending | 2026-10-29 07:57:59
H20261029063224EFEF | 李四 | 预算超支（市场部2026-10住宿剩余4400元，拟报5000元，超600元）且住宿标准超标（POL-001：上海上限500元/晚，2晚上限1000元，申报5000元，超标4000元，需部门负责人事前审批） | 5000.00 | pending | 2026-10-29 06:32:26
H202610291118324298 | - | 住宿费超标需部门负责人事前审批（POL-001：上海住宿上限500元/晚，申报800元/晚，超标300元） | 800.00 | pending | 2026-10-29 03:18:30
H202610291113001DB7 | 钱七 | 餐费申报 260 元超过 POL-002 餐补标准（100 元/天×2 天=200 元），超标 60 元；且无法确认是否为客户招待餐（需事前申请、人均≤200 元并注明客户单位与人数），信息不足无法判断 | 260.00 | pending | 2026-10-29 03:12:58
H20261029111228F52E | 王五 | 重复发票（POL-009）：INV-20261012-01 已在报销单 #1 使用，金额 900.00，状态 approved；同时住宿 700 元/晚超广州一线城市上限 500 元/晚（POL-001），超标 200 元需部门负责人事前审批 | 700.00 | pending | 2026-10-29 03:12:26

== 审计日志按工具/决策聚合 ==
policy_search | allowed | 72
escalate_to_human | pending_human | 62
budget_check | allowed | 60
voucher_create | allowed | 17
invoice_check | allowed | 8

== 最近 5 条审计记录 ==
2026-10-30 02:43:49 | web-0fbfb672 | budget_check | allowed
2026-10-30 02:43:44 | web-0fbfb672 | policy_search | allowed
2026-10-30 02:38:23 | ask-33b9a664 | budget_check | allowed
2026-10-30 02:38:20 | ask-33b9a664 | policy_search | allowed
2026-10-29 07:58:04 | web-c3a97166 | escalate_to_human | pending_human
```

## 怎么看这份数据

- `approvals.ticket_no`：`escalate_to_human` 生成的工单号，Web 界面「待人工」里显示的就是它。
- `approvals.reason`：转人工原因里带条款号（POL-001 / POL-002 / POL-009），可回查制度原文。
- `audit_logs.decision`：`allowed` 是正常执行，`pending_human` 是转人工；按工具聚合能看出每类工具被调用了多少次。
- `thread_id`：`web-xxxx` 来自页面会话，`ask-xxxx` / `chat-xxxx` 来自命令行脚本，便于按会话复盘。

> 库里的 62 张 pending 工单是逐日测试累积的，不是线上真实业务；正式部署时应对 `approvals` 加清理策略或状态流转。
