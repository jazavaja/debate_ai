import json
import requests
from .base import LLMProvider


class GenericProvider(LLMProvider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = self.base_uri
        self.headers = {
            self.auth_header_name: self._build_auth_value(),
            "Content-Type": "application/json"
        }

    def _build_url(self) -> str:
        if self.api_path:
            return f"{self.base_url}{self.api_path}" if self.api_path.startswith("/") else f"{self.base_url}/{self.api_path}"
        return self.base_url

    def _normalize_response(self, data: dict) -> str:
        if isinstance(data, dict):
            if "choices" in data and data["choices"]:
                first = data["choices"][0]
                if "message" in first and "content" in first["message"]:
                    return first["message"]["content"].strip()
                if "text" in first:
                    return first["text"].strip()
            if "content" in data and isinstance(data["content"], str):
                return data["content"].strip()
            if "response" in data:
                return str(data["response"]).strip()
        return json.dumps(data, ensure_ascii=False)

    def chat(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        url = self._build_url()
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
        return self._normalize_response(data)
