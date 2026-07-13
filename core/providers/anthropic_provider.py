import anthropic
from .base import LLMProvider


class AnthropicProvider(LLMProvider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = self.base_uri or "https://api.anthropic.com"
        self.client = anthropic.Anthropic(base_url=self.base_url, api_key=self.api_key)

    def chat(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        message = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return message.content[0].text.strip()

    def chat_stream(self, system_prompt: str, user_prompt: str, temperature: float, on_chunk):
        """
        استریم پاسخ با کمک context manager رسمی SDK. برای هر تکه متن، on_chunk صدا زده می‌شود.
        """
        with self.client.messages.stream(
            model=self.model,
            max_tokens=2000,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        ) as stream:
            for text in stream.text_stream:
                on_chunk(text)