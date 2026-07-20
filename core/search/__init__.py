"""
Search system package initialization.
مقداردهی اولیه بسته سیستم جستجو.
"""

from .base import SearchResult, BaseSearchProvider
from .config import SearchConfig, SearchProviderType
from .factory import SearchFactory
from .manager import SearchManager
from .providers import (
    DuckDuckGoProvider,
    TavilyProvider,
    SerperProvider,
    BingProvider,
    BraveProvider,
)

__all__ = [
    # Base classes and data structures
    "SearchResult",
    "BaseSearchProvider",
    
    # Configuration
    "SearchConfig",
    "SearchProviderType",
    
    # Factory
    "SearchFactory",
    
    # Manager (main interface)
    "SearchManager",
    
    # Providers
    "DuckDuckGoProvider",
    "TavilyProvider",
    "SerperProvider",
    "BingProvider",
    "BraveProvider",
]
