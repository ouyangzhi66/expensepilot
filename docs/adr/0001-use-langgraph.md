# ADR-001：用 LangGraph 而不是手写 while 循环

## 背景
报销 Agent 需要多轮状态、条件分支、人工中断和可恢复执行。

## 决策
使用 LangGraph 的 StateGraph + checkpointer。

## 后果
- 好处：状态显式、可中断 / 恢复、图可视化、便于评测。
- 代价：多一层框架学习；简单流程会显得重。

## 备选
- 手写 while + if：前期快，后期状态和中断难维护。
- Spring AI / LangChain4j：Java 栈更熟，但多步状态要自己写。
