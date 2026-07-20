"""
Configuration and enumerations for search system.
تنظیمات و تعریف‌های Enum برای سیستم جستجو.
"""

import os
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class SearchProviderType(Enum):
    """
    Enumeration of available search providers.
    تعریف انواع سرویس‌دهندگان جستجوی موجود.
    """
    DUCKDUCKGO = "duckduckgo"
    TAVILY = "tavily"
    SERPER = "serper"
    BING = "bing"
    BRAVE = "brave"


@dataclass
class SearchConfig:
    """
    Configuration for search system.
    تنظیمات سیستم جستجو.
    """
    active_provider: SearchProviderType = SearchProviderType.DUCKDUCKGO
    default_max_results: int = 3
    
    # API Keys
    tavily_api_key: Optional[str] = field(default_factory=lambda: os.getenv("TAVILY_API_KEY"))
    serper_api_key: Optional[str] = field(default_factory=lambda: os.getenv("SERPER_API_KEY"))
    bing_api_key: Optional[str] = field(default_factory=lambda: os.getenv("BING_SEARCH_API_KEY"))
    brave_api_key: Optional[str] = field(default_factory=lambda: os.getenv("BRAVE_SEARCH_API_KEY"))
    
    # Fallback settings
    enable_fallback: bool = True
    fallback_provider: SearchProviderType = SearchProviderType.DUCKDUCKGO
    
    def __post_init__(self):
        """
        Validate configuration after initialization.
        اعتبار‌سنجی تنظیمات پس از مقداردهی اولیه.
        """
        # Try to load active_provider from env if set
        env_provider = os.getenv("SEARCH_PROVIDER", "").lower()
        if env_provider:
            try:
                self.active_provider = SearchProviderType(env_provider)
            except ValueError:
                pass  # Keep default if invalid
        
        # Try to load default_max_results from env
        env_max_results = os.getenv("SEARCH_MAX_RESULTS")
        if env_max_results and env_max_results.isdigit():
            self.default_max_results = int(env_max_results)
