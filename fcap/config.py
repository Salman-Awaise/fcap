"""Configuration for the FCAP platform, read from the environment."""

import os
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
TEMPLATE_DIR = PACKAGE_ROOT / "templates"

# GPT-OSS-20B Configuration
# The token is read from the environment; never hardcode it in source.
HF_TOKEN = os.environ.get("HF_TOKEN", "")
BASE_URL = os.environ.get("HF_BASE_URL", "https://router.huggingface.co/v1")
MODEL = os.environ.get("HF_MODEL", "openai/gpt-oss-20b:fireworks-ai")

MAX_TOKENS = 200
TEMPERATURE = 0.7
REQUEST_TIMEOUT = 30

DB_PATH = os.environ.get("FCAP_DB_PATH", "robust_gpt_oss_platform.db")

HOST = os.environ.get("FCAP_HOST", "0.0.0.0")
PORT = int(os.environ.get("FCAP_PORT", "8000"))

CLINIC_PHONE = "(555) 123-4567"


def require_token() -> str:
    """Return the Hugging Face token, or explain how to set it."""
    if not HF_TOKEN:
        raise RuntimeError(
            "HF_TOKEN is not set. Export your Hugging Face token before starting:\n"
            "    export HF_TOKEN='your_huggingface_token_here'"
        )
    return HF_TOKEN
