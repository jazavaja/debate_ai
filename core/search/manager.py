"""
Search manager - main interface for the search system.
مدیر جستجو - رابط اصلی سیستم جستجو.
"""

import logging
from typing import Optional
from .base import SearchResult
from .config import SearchConfig, SearchProviderType
from .factory import SearchFactory
from .providers import (
    DuckDuckGoProvider,
    TavilyProvider,
    SerperProvider,
    BingProvider,
    BraveProvider,
)

logger = logging.getLogger(__name__)


class SearchManager:
    """
    Main search manager that provides search functionality to the debate engine.
    Implements automatic fallback to DuckDuckGo if primary provider fails.
    
    مدیر جستجوی اصلی که قابلیت جستجو را برای موتور مناظره فراهم می‌کند.
    فالبک خودکار به DuckDuckGo را در صورت شکست سرویس‌دهنده اولیه پیاده‌سازی می‌کند.
    """
    
    def __init__(self, config: Optional[SearchConfig] = None):
        """
        Initialize SearchManager.
        
        Args:
            config: Search configuration. If None, default config is created.
            
        مقداردهی اولیه SearchManager.
        
        آرگومان‌ها:
            config: تنظیمات جستجو. اگر None باشد، تنظیمات پیش‌فرض ایجاد می‌شود.
        """
        self.config = config or SearchConfig()
        self._register_providers()
        self.current_provider = None
        self._initialize_provider()
    
    def _register_providers(self) -> None:
        """
        Register all available search providers with the factory.
        
        تمام سرویس‌دهندگان جستجوی موجود را در Factory ثبت کنید.
        """
        SearchFactory.register(SearchProviderType.DUCKDUCKGO, DuckDuckGoProvider)
        SearchFactory.register(SearchProviderType.TAVILY, TavilyProvider)
        SearchFactory.register(SearchProviderType.SERPER, SerperProvider)
        SearchFactory.register(SearchProviderType.BING, BingProvider)
        SearchFactory.register(SearchProviderType.BRAVE, BraveProvider)
        
        logger.info("All search providers registered successfully")
    
    def _initialize_provider(self) -> None:
        """
        Initialize the current search provider based on config.
        
        سرویس‌دهنده جستجوی فعلی را بر اساس تنظیمات مقداردهی کنید.
        """
        try:
            self.current_provider = SearchFactory.create(
                self.config.active_provider,
                self.config
            )
            logger.info(f"Search provider initialized: {self.config.active_provider.value}")
        except Exception as e:
            logger.error(f"Failed to initialize provider {self.config.active_provider.value}: {str(e)}")
            self.current_provider = None
    
    def set_provider(self, provider_type: SearchProviderType) -> bool:
        """
        Switch to a different search provider.
        
        Args:
            provider_type: The provider type to switch to
            
        Returns:
            True if switch was successful, False otherwise
            
        جابجایی به سرویس‌دهنده جستجوی مختلف.
        
        آرگومان‌ها:
            provider_type: نوع سرویس‌دهنده برای جابجایی
            
        بازگشت:
            True اگر جابجایی موفق بود، False در غیر این صورت
        """
        try:
            provider = SearchFactory.create(provider_type, self.config)
            self.current_provider = provider
            self.config.active_provider = provider_type
            logger.info(f"Switched to search provider: {provider_type.value}")
            return True
        except Exception as e:
            logger.error(f"Failed to switch to provider {provider_type.value}: {str(e)}")
            return False
    
    def _search_with_provider(self, query: str, max_results: int) -> list:
        """
        Internal method to search with current provider.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of SearchResult objects
            
        روش داخلی برای جستجو با سرویس‌دهنده فعلی.
        
        آرگومان‌ها:
            query: کوئری جستجو
            max_results: حداکثر تعداد نتایج
            
        بازگشت:
            فهرستی از اشیاء SearchResult
        """
        if self.current_provider is None:
            logger.error("No search provider is initialized")
            return []
        
        try:
            results = self.current_provider.search(query, max_results)
            return results
        except Exception as e:
            logger.error(f"Error during search: {str(e)}")
            return []
    
    def search(self, query: str, max_results: Optional[int] = None) -> str:
        """
        Perform a search query with automatic fallback support.
        
        Args:
            query: Search query string
            max_results: Maximum number of results. If None, uses config default.
            
        Returns:
            Formatted markdown string with search results ready for LLM injection
            
        انجام کوئری جستجو با پشتیبانی فالبک خودکار.
        
        آرگومان‌ها:
            query: رشته کوئری جستجو
            max_results: حداکثر تعداد نتایج. اگر None، از پیش‌فرض تنظیمات استفاده می‌کند.
            
        بازگشت:
            رشته markdown قالب‌بندی‌شده با نتایج جستجو آماده برای تزریق به LLM
        """
        if not query or not query.strip():
            logger.warning("Empty search query provided")
            return "خطا: کوئری جستجو خالی است."
        
        max_results = max_results or self.config.default_max_results
        
        logger.info(f"Starting search with query: '{query}' (max_results={max_results})")
        
        # Try primary provider
        results = self._search_with_provider(query, max_results)
        
        # If primary provider failed and fallback is enabled
        if not results and self.config.enable_fallback and self.config.active_provider != self.config.fallback_provider:
            logger.warning(
                f"Primary provider {self.config.active_provider.value} returned no results. "
                f"Falling back to {self.config.fallback_provider.value}"
            )
            
            # Switch to fallback provider
            if self.set_provider(self.config.fallback_provider):
                results = self._search_with_provider(query, max_results)
            else:
                logger.error("Failed to switch to fallback provider")
        
        # Format and return results
        return self._format_results(query, results)
    
    def _format_results(self, query: str, results: list) -> str:
        """
        Format search results into markdown string for LLM injection.
        
        Args:
            query: Original search query
            results: List of SearchResult objects
            
        Returns:
            Formatted markdown string
            
        قالب‌بندی نتایج جستجو به رشته markdown برای تزریق به LLM.
        
        آرگومان‌ها:
            query: کوئری جستجوی اصلی
            results: فهرستی از اشیاء SearchResult
            
        بازگشت:
            رشته markdown قالب‌بندی‌شده
        """
        if not results:
            return f"نتیجه‌ای برای کوئری '{query}' یافت نشد."
        
        markdown = f"## نتایج جستجو برای: '{query}'\n\n"
        markdown += f"تعداد نتایج: {len(results)}\n"
        markdown += f"منبع: {results[0].source_provider}\n\n"
        
        for idx, result in enumerate(results, 1):
            markdown += f"### نتیجه {idx}\n"
            markdown += f"**عنوان:** {result.title}\n\n"
            markdown += f"**توضیح:** {result.body}\n\n"
            markdown += f"**لینک:** [{result.url}]({result.url})\n\n"
        
        return markdown
    
    def get_active_provider(self) -> str:
        """
        Get the name of the currently active search provider.
        
        Returns:
            Name of active provider
            
        نام سرویس‌دهنده فعال فعلی را دریافت کنید.
        
        بازگشت:
            نام سرویس‌دهنده فعال
        """
        return self.config.active_provider.value if self.config.active_provider else "None"
    
    def get_available_providers(self) -> list:
        """
        Get list of all available provider types.
        
        Returns:
            List of SearchProviderType enum values
            
        فهرست تمام انواع سرویس‌دهندگان موجود را دریافت کنید.
        
        بازگشت:
            فهرستی از مقادیر enum SearchProviderType
        """
        return SearchFactory.get_registered_providers()
