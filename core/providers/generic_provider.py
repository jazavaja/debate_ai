from openai import OpenAI
from .base import LLMProvider


class GenericProvider(LLMProvider):
    """
    برای هر API سازگار با OpenAI (base_uri دلخواه + هدر auth دلخواه).
    از SDK رسمی openai استفاده می‌کند؛ فقط هدر احراز هویت را override می‌کنیم
    چون ممکن است اسم هدر با "Authorization" فرق داشته باشد.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # مهم: base_url فقط باید ریشه API باشه (مثلاً https://openrouter.ai/api/v1)
        # چون خود SDK مسیر /chat/completions رو خودکار اضافه می‌کنه.
        # اگه api_path رو هم بهش بچسبونیم، مسیر دوبار تکرار میشه و 404 می‌گیریم.
        self.base_url = self.base_uri
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key or "not-needed",
            default_headers={self.auth_header_name: self._build_auth_value()},
        )

    def _normalize_response(self, completion, think: bool = False) -> str:
        """
        بعضی APIهای سازگار با OpenAI فیلدهای اضافی مثل reasoning/thinking
        برمی‌گردانند که در schema رسمی SDK نیست. این‌ها را از model_extra می‌خوانیم.
        """
        message = completion.choices[0].message
        text = (message.content or "").strip()

        if think:
            extra = getattr(message, "model_extra", None) or {}
            reasoning = (
                extra.get("reasoning")
                or extra.get("thinking")
                or extra.get("reasoning_content")
                or ""
            ).strip()
            if reasoning:
                return f"{reasoning}\n\n{text}" if text else reasoning

        return text

    def chat(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=2000,
        )
        return self._normalize_response(completion)

    def chat_stream(self, system_prompt: str, user_prompt: str, temperature: float, on_chunk):
        """
        تلاش برای استریم؛ اگر سرور استریم را پشتیبانی نکرد یا خطا داد،
        به‌صورت fallback کل پاسخ را یکجا با on_chunk می‌فرستیم.
        """
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=2000,
                stream=True,
            )

            any_chunk = False
            for chunk in stream:
                if not getattr(chunk, "choices", None):
                    continue
                delta = chunk.choices[0].delta
                content = getattr(delta, "content", None)
                if content:
                    on_chunk(content)
                    any_chunk = True

            if any_chunk:
                return

        except Exception:
            pass

        on_chunk(self.chat(system_prompt, user_prompt, temperature))