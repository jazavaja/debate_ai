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

    import json

    def _normalize_response(self, data, think: bool = False) -> str:
        """
        Normalize responses from OpenAI-compatible APIs.

        Parameters
        ----------
        data : dict | object
            Raw response.
        think : bool
            If True, append reasoning/thinking when available.

        Returns
        -------
        str
        """

        # Convert SDK objects to dict
        if hasattr(data, "model_dump"):
            data = data.model_dump()
        elif hasattr(data, "dict"):
            data = data.dict()

        if not isinstance(data, dict):
            return str(data)

        choices = data.get("choices") or []
        if not choices:
            return (
                    data.get("content")
                    or data.get("response")
                    or json.dumps(data, ensure_ascii=False)
            )

        first = choices[0]

        # ---------- content ----------
        text = ""

        message = first.get("message")

        if isinstance(message, dict):
            content = message.get("content")

            if isinstance(content, str):
                text = content.strip()

            elif isinstance(content, list):
                parts = []

                for item in content:
                    if isinstance(item, dict):
                        if item.get("type") == "text":
                            parts.append(item.get("text", ""))

                text = "\n".join(parts).strip()

        elif "text" in first:
            text = str(first["text"]).strip()

        # ---------- reasoning ----------
        if think:

            reasoning = ""

            if isinstance(message, dict):
                reasoning = (
                        message.get("reasoning")
                        or message.get("thinking")
                        or message.get("reasoning_content")
                        or ""
                )

            reasoning = reasoning.strip()

            if reasoning:
                if text:
                    return f"{reasoning}\n\n{text}"
                return reasoning

        return text

    def chupat(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
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

        print("Raw LLM response:", data)
        return self._normalize_response(data)
