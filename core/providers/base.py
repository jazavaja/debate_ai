from abc import ABC, abstractmethod
from typing import Callable


class LLMProvider(ABC):
    def __init__(
        self,
        base_uri: str,
        api_key: str,
        model: str,
        auth_header_name: str,
        auth_token_prefix: str,
        api_path: str,
    ):
        self.base_uri = base_uri.rstrip("/") if base_uri else ""
        self.api_key = api_key
        self.model = model
        self.auth_header_name = auth_header_name
        self.auth_token_prefix = auth_token_prefix
        self.api_path = api_path

    def _build_auth_value(self) -> str:
        prefix = self.auth_token_prefix or ""
        if prefix.lower() == "bearer" and not prefix.endswith(" "):
            prefix = f"{prefix} "
        return f"{prefix}{self.api_key}" if prefix else self.api_key

    @abstractmethod
    def chat(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        raise NotImplementedError
    
    @abstractmethod
    def chat_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        on_chunk: Callable[[str], None],
    ) -> None:
        """
        Stream the chat response. Call `on_chunk(chunk)` for every received text chunk.
        Implementations should perform network streaming and invoke the callback
        as soon as each piece of text is available.
        """
        raise NotImplementedError
