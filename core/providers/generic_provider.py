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

    def chat(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        """
        Synchronous chat implementation for generic providers.
        Uses the existing `chupat` request path.
        """
        return self.chupat(system_prompt, user_prompt, temperature)

    def chat_stream(self, system_prompt: str, user_prompt: str, temperature: float, on_chunk):
        """
        Fallback streaming for generic providers: if the remote API doesn't
        support streaming, call the synchronous `chat` and emit the full
        response as a single chunk via `on_chunk`.
        """
        try:
            url = self._build_url()
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
                any_chunk = False
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

                    content = None
                    choice = parsed.get("choices", [{}])[0]
                    delta = choice.get("delta", {}) or {}
                    content = delta.get("content") or delta.get("text")
                    if content is None:
                        message = choice.get("message", {})
                        if isinstance(message, dict):
                            content = message.get("content") or message.get("text")
                    if content is None:
                        content = parsed.get("content") or parsed.get("text")
                    if isinstance(content, str) and content:
                        on_chunk(content)
                        any_chunk = True

                if any_chunk:
                    return

        except Exception:
            pass

        full = self.chat(system_prompt, user_prompt, temperature)
        on_chunk(full)
