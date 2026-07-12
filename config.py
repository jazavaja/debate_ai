# config.py
import os

# LLM Configuration - می‌تونی API key رو اینجا بذاری یا از env بخونی
LLM_PROVIDER = "openai"  # یا "anthropic", "local"
LLM_MODEL = "gpt-4o-mini"  # یا مدل دلخواه
LLM_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here")

# Debate Settings
MAX_TURNS_DEFAULT = 50
TEMPERATURE = 0.8

# UI Settings
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900