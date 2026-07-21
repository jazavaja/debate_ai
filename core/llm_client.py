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
import time
import requests
from typing import Callable, Optional


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

        # Fallback providers list (from settings)
        self._fallback_providers: list[dict] = []
        self._max_fallback_retries: int = 3
        self._current_fallback_index: int = 0

    def apply_settings(self, providers_list: list[dict], max_retries: int = 3):
        """
        اعمال تنظیمات fallback providers از Settings

        Args:
            providers_list: لیست dicts شامل provider, model, api_key, base_uri, ...
            max_retries: حداکثر تعداد providers برای تلاش
        """
        self._fallback_providers = providers_list
        self._max_fallback_retries = max_retries
        self._current_fallback_index = 0

        if providers_list:
            first = providers_list[0]
            self._apply_provider(first)

    def _apply_provider(self, provider_data: dict):
        """اعمال یک provider خاص"""
        self.provider = provider_data.get("provider", "openai")
        self.api_key = provider_data.get("api_key", "")
        self.model = provider_data.get("model", "gpt-4o-mini")
        self.base_uri = provider_data.get("base_uri", "https://api.openai.com/v1")
        self.auth_header_name = provider_data.get("auth_header_name", "Authorization")
        self.auth_token_prefix = provider_data.get("auth_token_prefix", "Bearer ")
        self.api_path = provider_data.get("api_path", "/chat/completions")

        self.provider_impl = create_provider(
            provider_name=self.provider,
            base_uri=self.base_uri,
            api_key=self.api_key,
            model=self.model,
            auth_header_name=self.auth_header_name,
            auth_token_prefix=self.auth_token_prefix,
            api_path=self.api_path,
        )

    def get_current_provider_info(self) -> str:
        """اطلاعات provider فعلی"""
        return f"{self.provider} / {self.model}"

    def _try_next_fallback(self) -> bool:
        """تلاش provider بعدی در لیست fallback"""
        self._current_fallback_index += 1
        if self._current_fallback_index >= len(self._fallback_providers):
            self._current_fallback_index = 0
            return False
        next_provider = self._fallback_providers[self._current_fallback_index]
        self._apply_provider(next_provider)
        return True

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


    def optimize_prompt(self, original_prompt: str, purpose: str, name: str = "") -> str:
        """
        بهینه‌سازی پرامپت با استفاده از LLM

        Args:
            original_prompt: پرامپت اصلی کاربر
            purpose: هدف پرامپت (مثلاً 'debater', 'moderator')
            name: نام شخصیت

        Returns:
            پرامپت بهینه‌شده
        """
        purpose_text = "مذاکره‌کننده" if purpose == "debater" else "مجری" if purpose == "moderator" else purpose
        name_part = f"\nنام شخصیت: {name}" if name else ""
        
        optimization_system = """شما یک متخصص Prompt Engineering هستید. پرامپت داده شده را برای استفاده در یک مناظره هوش مصنوعی بهینه کنید.

قوانین بهینه‌سازی:
1. شخصیت باید کاملاً مشخص و قابل تمایز باشد
2. لحن و سبک گفتار باید تعریف شود
3. دیدگاه‌های کلیدی باید مشخص باشند
4. از کلی‌گویی پرهیز کنید
5. پرامپت باید به زبان فارسی باشد
6. اگر نام داده شده، آن نام را به‌طور مشخص درسیستم پرامپت استفاده کن

فقط پرامپت بهینه‌شده را خروجی بده، بدون هیچ توضیح اضافی."""

        optimization_user = f"""نوع شخصیت: {purpose_text}{name_part}
پرامپت فعلی:
{original_prompt}

لطفاً این پرامپت را بهینه کنید:"""

        return self.chat(optimization_system, optimization_user, temperature=0.3)

    def optimize_prompt_stream(self, original_prompt: str, purpose: str, on_chunk, name: str = "", temperature: float = 0.3):
        """
        بهینه‌سازی پرامپت به صورت streaming

        Args:
            original_prompt: پرامپت اصلی کاربر
            purpose: هدف پرامپت ('debater', 'moderator')
            on_chunk: callback برای دریافت چانک‌ها
            name: نام شخصیت
            temperature: میزان خلاقیت
        """
        purpose_text = "مذاکره‌کننده" if purpose == "debater" else "مجری" if purpose == "moderator" else purpose
        name_part = f"\nنام شخصیت: {name}" if name else ""
        
        optimization_system = """شما یک متخصص Prompt Engineering هستید. پرامپت داده شده را برای استفاده در یک مناظره هوش مصنوعی بهینه کنید.

قوانین بهینه‌سازی:
1. شخصیت باید کاملاً مشخص و قابل تمایز باشد
2. لحن و سبک گفتار باید تعریف شود
3. دیدگاه‌های کلیدی باید مشخص باشند
4. از کلی‌گویی پرهیز کنید
5. پرامپت باید به زبان فارسی باشد
6. اگر نام داده شده، آن نام را به‌طور مشخص در سیستم پرامپت استفاده کن

فقط پرامپت بهینه‌شده را خروجی بده، بدون هیچ توضیح اضافی."""

        optimization_user = f"""نوع شخصیت: {purpose_text}{name_part}
پرامپت فعلی:
{original_prompt}

لطفاً این پرامپت را بهینه کنید:"""

        self.chat_stream(optimization_system, optimization_user, on_chunk, temperature)

    def _is_retryable_exception(self, e: Exception) -> bool:
        # Network / transient HTTP errors and explicit ResourceExhausted
        if isinstance(e, requests.exceptions.Timeout):
            return True
        if isinstance(e, requests.exceptions.RequestException):
            status = None
            if getattr(e, "response", None) is not None:
                status = getattr(e.response, "status_code", None)
            if status in (502, 503, 504):
                return True
        if "ResourceExhausted" in str(e) or "resource exhausted" in str(e).lower():
            return True
        return False

    def chat_stream(
        self,
        system_prompt,
        user_prompt,
        on_chunk,
        temperature=TEMPERATURE,
        raise_on_error: bool = False,
    ):
        # Retry for the current provider
        max_retries = 3
        delays = [8, 16, 32]

        for attempt in range(max_retries):
            got_any_chunk = False

            def tracking_on_chunk(text):
                nonlocal got_any_chunk
                got_any_chunk = True
                on_chunk(text)

            try:
                self.provider_impl.chat_stream(
                    system_prompt, user_prompt, temperature, tracking_on_chunk
                )
                return
            except Exception as e:
                if got_any_chunk:
                    msg = f"خطا در ادامه استریم: {str(e)}"
                    if raise_on_error:
                        raise RuntimeError(msg) from e
                    on_chunk(f"\n[{msg}]")
                    return
                if self._is_retryable_exception(e) and attempt < max_retries - 1:
                    time.sleep(delays[attempt])
                    continue

                # Fallback to next provider if available
                if self._fallback_providers and self._try_next_fallback():
                    on_chunk(f"\n[تلاش با provider بعدی: {self.get_current_provider_info()}...]\n")
                    # Reset retry count for new provider
                    for fb_attempt in range(max_retries):
                        got_any_chunk_fb = False

                        def tracking_on_chunk_fb(text):
                            nonlocal got_any_chunk_fb
                            got_any_chunk_fb = True
                            on_chunk(text)

                        try:
                            self.provider_impl.chat_stream(
                                system_prompt, user_prompt, temperature, tracking_on_chunk_fb
                            )
                            return
                        except Exception as fb_e:
                            if got_any_chunk_fb:
                                msg = f"خطا در ادامه استریم: {str(fb_e)}"
                                if raise_on_error:
                                    raise RuntimeError(msg) from fb_e
                                on_chunk(f"\n[{msg}]")
                                return
                            if self._is_retryable_exception(fb_e) and fb_attempt < max_retries - 1:
                                time.sleep(delays[fb_attempt])
                                continue
                            # Try next fallback
                            if self._fallback_providers and self._try_next_fallback():
                                on_chunk(f"\n[تلاش با provider بعدی: {self.get_current_provider_info()}...]\n")
                                continue
                            if raise_on_error:
                                raise
                            on_chunk(f"[خطا در LLM: {str(fb_e)}]")
                            return
                    return

                if raise_on_error:
                    raise
                on_chunk(f"[خطا در LLM: {str(e)}]")
                return