"""Check the Postgres / pgvector connection."""

import os

import psycopg
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("DATABASE_URL")
if not url:
    raise SystemExit("DATABASE_URL is not set. Copy .env.example to .env first.")

with psycopg.connect(url) as conn, conn.cursor() as cur:
    cur.execute("select version();")
    print(cur.fetchone()[0])
    cur.execute("select extname from pg_extension where extname = 'vector';")
    print("pgvector:", bool(cur.fetchone()))
