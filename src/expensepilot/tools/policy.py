"""policy_search: wrap the D02 clause retriever as an LLM tool."""

from langchain_core.tools import tool

from expensepilot.rag import search


@tool
def policy_search(query: str) -> str:
    """查询财务报销制度条款。

    输入一个具体的制度问题（例如“上海住宿标准是多少”），返回最相关的 3 条条款，
    每条包含条款号、标题、相似度和原文。只在需要核对报销规则时调用。
    """
    results = search(query, k=3)
    if not results:
        return "没有找到相关制度条款。"

    blocks = []
    for policy_no, title, clause_no, content, score in results:
        blocks.append(
            f"[{policy_no} {clause_no}] {title}（相似度 {score:.3f}）\n{content}"
        )
    return "\n\n".join(blocks)
