"""Check the configured OpenAI-compatible chat model."""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY", "").strip()
base_url = os.getenv("OPENAI_BASE_URL", "").strip()
model = os.getenv("MODEL_NAME", "").strip()

if not api_key or api_key == "sk-xxx":
    raise SystemExit("OPENAI_API_KEY is not set; edit .env first.")

client = OpenAI(api_key=api_key, base_url=base_url)
try:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "只回复两个字：ok"}],
        max_tokens=10,
        temperature=0,
    )
except Exception as exc:
    raise SystemExit(f"LLM call failed: {type(exc).__name__}: {exc}") from exc

print("model:", model)
print("reply:", (response.choices[0].message.content or "").strip())
