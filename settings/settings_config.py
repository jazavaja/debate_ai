# settings/settings_config.py
from dataclasses import dataclass, field, asdict
from typing import List


@dataclass
class LLMProviderConfig:
    """تنظیمات یک LLM Provider"""
    name: str
    provider: str  # openai, anthropic, gemini, custom
    model: str
    api_key: str
    base_uri: str
    auth_header_name: str = "Authorization"
    auth_token_prefix: str = "Bearer "
    temperature: float = 0.8
    priority: int = 1  # اولویت (1 = بالاترین)
    enabled: bool = True
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @staticmethod
    def from_dict(data: dict) -> "LLMProviderConfig":
        return LLMProviderConfig(**data)


@dataclass
class SettingsConfig:
    """تنظیمات اصلی برنامه"""
    llm_providers: List[LLMProviderConfig] = field(default_factory=list)
    max_retries: int = 3  # حداکثر تعداد providers برای تلاش
    
    def to_dict(self) -> dict:
        return {
            "llm_providers": [p.to_dict() for p in self.llm_providers],
            "max_retries": self.max_retries,
        }
    
    @staticmethod
    def from_dict(data: dict) -> "SettingsConfig":
        providers = [
            LLMProviderConfig.from_dict(p)
            for p in data.get("llm_providers", [])
        ]
        return SettingsConfig(
            llm_providers=providers,
            max_retries=data.get("max_retries", 3),
        )
    
    def get_sorted_providers(self) -> List[LLMProviderConfig]:
        """دریافت providers به ترتیب اولویت"""
        enabled = [p for p in self.llm_providers if p.enabled]
        return sorted(enabled, key=lambda p: p.priority)
    
    def get_provider_by_name(self, name: str) -> LLMProviderConfig | None:
        for p in self.llm_providers:
            if p.name == name:
                return p
        return None
