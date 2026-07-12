# config.py
import os
from pathlib import Path


def _load_dotenv() -> None:
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


_load_dotenv()

# LLM Configuration - می‌توانید تنظیمات LLM را از محیط (env) یا اینجا وارد کنید
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()  # یا anthropic, custom, local
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_API_KEY = os.getenv("LLM_API_KEY", os.getenv("OPENAI_API_KEY", "your-api-key-here"))
LLM_BASE_URI = os.getenv("LLM_BASE_URI", os.getenv("OPENAI_BASE_URI", "https://api.openai.com/v1"))
LLM_AUTH_HEADER_NAME = os.getenv("LLM_AUTH_HEADER_NAME", "Authorization")
LLM_AUTH_TOKEN_PREFIX = os.getenv("LLM_AUTH_TOKEN_PREFIX", "Bearer ")
LLM_API_PATH = os.getenv("LLM_API_PATH", "/chat/completions")

# Debate Settings
MAX_TURNS_DEFAULT = 50
TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.8"))

# UI Settings
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900