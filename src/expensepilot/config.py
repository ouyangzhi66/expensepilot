"""Environment configuration."""

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

# Keep model downloads inside the project; C:\ root is not writable in this sandbox.
os.environ.setdefault("HF_HOME", str(PROJECT_ROOT / ".cache" / "hf"))
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "").strip()
MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-chat").strip()
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5").strip()
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "512"))
FASTEMBED_CACHE_PATH = os.getenv(
    "FASTEMBED_CACHE_PATH", str(PROJECT_ROOT / ".cache" / "fastembed")
)
