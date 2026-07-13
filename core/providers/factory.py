from .gemini_provider import GeminiProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .generic_provider import GenericProvider


PROVIDER_MAP = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "gemini": GeminiProvider,
}


def create_provider(
    provider_name: str,
    base_uri: str,
    api_key: str,
    model: str,
    auth_header_name: str,
    auth_token_prefix: str,
    api_path: str,
):
    provider_cls = PROVIDER_MAP.get(provider_name.lower(), GenericProvider)
    return provider_cls(
        base_uri=base_uri,
        api_key=api_key,
        model=model,
        auth_header_name=auth_header_name,
        auth_token_prefix=auth_token_prefix,
        api_path=api_path,
    )
