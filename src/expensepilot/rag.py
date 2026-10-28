"""Policy RAG: clause-level ingestion and cosine retrieval."""

from __future__ import annotations

import argparse
from typing import TYPE_CHECKING

import psycopg
from pgvector.psycopg import register_vector

from expensepilot.config import (
    DATABASE_URL,
    EMBEDDING_DIM,
    EMBEDDING_MODEL,
    FASTEMBED_CACHE_PATH,
)
from expensepilot.text import split_clauses

if TYPE_CHECKING:
    from fastembed import TextEmbedding

_model: TextEmbedding | None = None


def get_model() -> TextEmbedding:
    """Load the embedding model once per process."""
    global _model
    if _model is None:
        # Import lazily so config.py can set HF_HOME / HF_HUB_DISABLE_XET first.
        from fastembed import TextEmbedding

        _model = TextEmbedding(
            model_name=EMBEDDING_MODEL,
            cache_dir=FASTEMBED_CACHE_PATH,
        )
    return _model


def embed(texts: list[str]) -> list[list[float]]:
    vectors = [vector.tolist() for vector in get_model().embed(texts)]
    if vectors and len(vectors[0]) != EMBEDDING_DIM:
        raise RuntimeError(
            f"embedding dimension {len(vectors[0])} != EMBEDDING_DIM {EMBEDDING_DIM}"
        )
    return vectors


def connect() -> psycopg.Connection:
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set; copy .env.example to .env")
    conn = psycopg.connect(DATABASE_URL)
    register_vector(conn)
    return conn


def ingest() -> tuple[int, int]:
    """Embed every policy clause and upsert it into policy_chunks."""
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            "select id, policy_no, title, content from policies order by policy_no"
        )
        policies = cur.fetchall()

        rows = []
        for policy_id, policy_no, title, content in policies:
            for index, clause in enumerate(split_clauses(content), start=1):
                rows.append(
                    (
                        policy_id,
                        policy_no,
                        title,
                        f"{policy_no}-{index}",
                        clause,
                        f"{title}\n{clause}",
                    )
                )

        vectors = embed([row[5] for row in rows])

        for row, vector in zip(rows, vectors):
            cur.execute(
                """
                insert into policy_chunks
                    (policy_id, policy_no, title, clause_no, content, embedding)
                values (%s, %s, %s, %s, %s, %s)
                on conflict (policy_id, clause_no) do update set
                    title = excluded.title,
                    content = excluded.content,
                    embedding = excluded.embedding
                """,
                (*row[:5], vector),
            )
        conn.commit()
    return len(policies), len(rows)


def search(query: str, k: int = 3) -> list[tuple]:
    """Return the top-k clauses by cosine distance."""
    vector = embed([query])[0]
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """
            select policy_no, title, clause_no, content,
                   1 - (embedding <=> %s::vector) as score
            from policy_chunks
            order by embedding <=> %s::vector
            limit %s
            """,
            (vector, vector, k),
        )
        return cur.fetchall()


def main() -> None:
    parser = argparse.ArgumentParser(description="Policy RAG")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("ingest", help="embed policies into policy_chunks")

    search_parser = sub.add_parser("search", help="search policy clauses")
    search_parser.add_argument("query")
    search_parser.add_argument("-k", type=int, default=3)

    args = parser.parse_args()
    if args.command == "ingest":
        policies, chunks = ingest()
        print(f"ingested {chunks} chunks from {policies} policies")
    else:
        for policy_no, title, clause_no, content, score in search(args.query, args.k):
            print(f"[{score:.3f}] {policy_no} {clause_no} {title}")
            print(f"  {content}")


if __name__ == "__main__":
    main()
