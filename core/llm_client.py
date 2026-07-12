# core/llm_client.py
from config import (
    LLM_API_KEY,
    LLM_MODEL,
    LLM_PROVIDER,
    LLM_BASE_URI,
    LLM_AUTH_HEADER_NAME,
    LLM_AUTH_TOKEN_PREFIX,
    LLM_API_PATH,
    TEMPERATURE,
)
from .providers import create_provider


class LLMClient:
    """
    کلاینت LLM با الگوی Strategy
    می‌تونه OpenAI، Anthropic یا Local LLM رو پشتیبانی کنه
    """

    def __init__(self, provider: str = LLM_PROVIDER, api_key: str = LLM_API_KEY):
        self.provider = provider
        self.api_key = api_key
        self.model = LLM_MODEL
        self.base_uri = LLM_BASE_URI
        self.auth_header_name = LLM_AUTH_HEADER_NAME
        self.auth_token_prefix = LLM_AUTH_TOKEN_PREFIX
        self.api_path = LLM_API_PATH

        self.provider_impl = create_provider(
            provider_name=self.provider,
            base_uri=self.base_uri,
            api_key=self.api_key,
            model=self.model,
            auth_header_name=self.auth_header_name,
            auth_token_prefix=self.auth_token_prefix,
            api_path=self.api_path,
        )

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
            return self.provider_impl.chat(system_prompt, user_prompt, temperature)
        except Exception as e:
            return f"[خطا در اتصال به LLM: {str(e)}]"


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