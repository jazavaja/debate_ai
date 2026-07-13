import requests
import json
from .base import LLMProvider


class OpenAIProvider(LLMProvider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = self.base_uri or "https://api.openai.com/v1"
        self.headers = {
            self.auth_header_name: self._build_auth_value(),
            "Content-Type": "application/json"
        }

    def chat(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
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
        return data["choices"][0]["message"]["content"].strip()

    def chat_stream(self, system_prompt: str, user_prompt: str, temperature: float, on_chunk):
        """
        Stream response from OpenAI Chat Completions. Calls `on_chunk(str)` for each
        received text fragment. Parses Server-Sent Events style streaming lines.
        """
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": 2000,
            "stream": True
        }

        with requests.post(url, headers=self.headers, json=payload, stream=True, timeout=60) as resp:
            resp.raise_for_status()
            for raw_line in resp.iter_lines(decode_unicode=False):
                if not raw_line:
                    continue
                line = raw_line.decode("utf-8", errors="replace").strip()
                if not line.startswith("data:"):
                    continue
                data_str = line[len("data:"):].strip()
                if data_str == "[DONE]":
                    break
                try:
                    parsed = json.loads(data_str)
                except json.JSONDecodeError:
                    continue

                choice = parsed.get("choices", [{}])[0]
                delta = choice.get("delta", {}) or {}
                content = delta.get("content") or delta.get("text")
                if content is None:
                    message = choice.get("message", {})
                    if isinstance(message, dict):
                        content = message.get("content") or message.get("text")
                if isinstance(content, str) and content:
                    on_chunk(content)
