"""Environment configuration."""

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

SECRET_KEYS = (
    "DATABASE_URL",
    "OPENAI_API_KEY",
    "OPENAI_BASE_URL",
    "MODEL_NAME",
    "EMBEDDING_MODEL",
    "EMBEDDING_DIM",
    "HF_ENDPOINT",
    "FASTEMBED_CACHE_PATH",
)


def _load_streamlit_secrets() -> None:
    """On Streamlit Cloud, copy st.secrets into env before other imports."""
    try:
        import streamlit as st

        secrets = st.secrets.to_dict()
    except Exception:  # noqa: BLE001 - CLI/bare mode has no secrets
        return

    for key in SECRET_KEYS:
        if key not in os.environ and key in secrets:
            os.environ[key] = str(secrets[key])


_load_streamlit_secrets()

if os.name == "nt":
    DEFAULT_HF_HOME = PROJECT_ROOT / ".cache" / "hf"
    DEFAULT_FASTEMBED_CACHE = PROJECT_ROOT / ".cache" / "fastembed"
else:
    # Streamlit Community Cloud has an ephemeral, writable /tmp.
    DEFAULT_HF_HOME = Path("/tmp/hf")
    DEFAULT_FASTEMBED_CACHE = Path("/tmp/fastembed")

os.environ.setdefault("HF_HOME", str(DEFAULT_HF_HOME))
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "").strip()
MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-chat").strip()
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5").strip()
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "512"))
FASTEMBED_CACHE_PATH = os.getenv(
    "FASTEMBED_CACHE_PATH", str(DEFAULT_FASTEMBED_CACHE)
)
