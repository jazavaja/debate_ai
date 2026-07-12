# core/llm_client.py
import json
import requests
from typing import Optional, Dict, Any
from config import LLM_API_KEY, LLM_MODEL, LLM_PROVIDER, TEMPERATURE


class LLMClient:
    """
    کلاینت LLM با الگوی Strategy
    می‌تونه OpenAI، Anthropic یا Local LLM رو پشتیبانی کنه
    """

    def __init__(self, provider: str = LLM_PROVIDER, api_key: str = LLM_API_KEY):
        self.provider = provider
        self.api_key = api_key
        self.model = LLM_MODEL

        self._setup_endpoints()

    def _setup_endpoints(self):
        if self.provider == "openai":
            self.base_url = "https://api.openai.com/v1"
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        elif self.provider == "anthropic":
            self.base_url = "https://api.anthropic.com/v1"
            self.headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            }
        else:
            raise ValueError(f"Provider {self.provider} پشتیبانی نمی‌شود")

    def chat(self, system_prompt: str, user_prompt: str, temperature: float = TEMPERATURE) -> str:
        """
        ارسال پیام به LLM و دریافت پاسخ

        Args:
            system_prompt: دستورالعمل سیستم
            user_prompt: پیام کاربر
            temperature: میزان خلاقیت (۰ تا ۱)

        Returns:
            پاسخ متنی LLM
        """
        try:
            if self.provider == "openai":
                return self._call_openai(system_prompt, user_prompt, temperature)
            elif self.provider == "anthropic":
                return self._call_anthropic(system_prompt, user_prompt, temperature)
        except Exception as e:
            return f"[خطا در اتصال به LLM: {str(e)}]"

    def _call_openai(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        url = f"{self.base_url}/chat/completions"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": 2000
        }

        response = requests.post(url, headers=self.headers, json=payload, timeout=60)
        response.raise_for_status()

        data = response.json()
        return data['choices'][0]['message']['content'].strip()

    def _call_anthropic(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        url = f"{self.base_url}/messages"

        payload = {
            "model": self.model,
            "max_tokens": 2000,
            "temperature": temperature,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}]
        }

        response = requests.post(url, headers=self.headers, json=payload, timeout=60)
        response.raise_for_status()

        data = response.json()
        return data['content'][0]['text'].strip()

    def optimize_prompt(self, original_prompt: str, purpose: str) -> str:
        """
        بهینه‌سازی پرامپت با استفاده از LLM

        Args:
            original_prompt: پرامپت اصلی کاربر
            purpose: هدف پرامپت (مثلاً 'debater', 'moderator')

        Returns:
            پرامپت بهینه‌شده
        """
        optimization_system = """شما یک متخصص Prompt Engineering هستید. پرامپت داده شده را برای استفاده در یک مناظره هوش مصنوعی بهینه کنید.

قوانین بهینه‌سازی:
1. شخصیت باید کاملاً مشخص و قابل تمایز باشد
2. لحن و سبک گفتار باید تعریف شود
3. دیدگاه‌های کلیدی باید مشخص باشند
4. از کلی‌گویی پرهیز کنید
5. پرامپت باید به زبان فارسی باشد

فقط پرامپت بهینه‌شده را خروجی بده، بدون هیچ توضیح اضافی."""

        optimization_user = f"""هدف: {purpose}
پرامپت فعلی:
{original_prompt}

لطفاً این پرامپت را بهینه کنید:"""

        return self.chat(optimization_system, optimization_user, temperature=0.3)