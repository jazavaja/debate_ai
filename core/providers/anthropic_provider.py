import requests
import json
from .base import LLMProvider


class AnthropicProvider(LLMProvider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = self.base_uri or "https://api.anthropic.com/v1"
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }

    def chat(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
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
        return data["content"][0]["text"].strip()

    def chat_stream(self, system_prompt: str, user_prompt: str, temperature: float, on_chunk):
        """
        Stream response from Anthropic. Calls `on_chunk(str)` for each text fragment.
        Uses line-delimited JSON or simple text chunks depending on the API.
        """
        url = f"{self.base_url}/messages"
        payload = {
            "model": self.model,
            "max_tokens": 2000,
            "temperature": temperature,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
            "stream": True
        }

        with requests.post(url, headers=self.headers, json=payload, stream=True, timeout=60) as resp:
            resp.raise_for_status()
            for raw_line in resp.iter_lines(decode_unicode=False):
                if not raw_line:
                    continue
                line = raw_line.decode("utf-8", errors="replace").strip()
                if line.startswith("data:"):
                    data_str = line[len("data:"):].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        parsed = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue
                else:
                    try:
                        parsed = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                text = None
                if "delta" in parsed:
                    text = parsed.get("delta", {}).get("content")
                if not text:
                    text = parsed.get("text") or parsed.get("content")
                if not text:
                    message = parsed.get("message")
                    if isinstance(message, dict):
                        text = message.get("content") or message.get("text")
                if isinstance(text, str) and text:
                    on_chunk(text)
