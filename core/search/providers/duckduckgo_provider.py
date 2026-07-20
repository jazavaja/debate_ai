"""
DuckDuckGo search provider implementation.
پیاده‌سازی سرویس‌دهنده جستجوی DuckDuckGo.
"""

import logging
from typing import List
from ..base import BaseSearchProvider, SearchResult
from ..config import SearchConfig

try:
    from ddgs import DDGS
except ImportError:
    DDGS = None

logger = logging.getLogger(__name__)


class DuckDuckGoProvider(BaseSearchProvider):
    """
    DuckDuckGo search provider implementation.
    Free and does not require API keys.
    
    پیاده‌سازی سرویس‌دهنده جستجوی DuckDuckGo.
    رایگان و نیاز به کلیدهای API ندارد.
    """
    
    def __init__(self, config: SearchConfig):
        """
        Initialize DuckDuckGo provider.
        
        Args:
            config: Search configuration object
            
        مقداردهی اولیه سرویس‌دهنده DuckDuckGo.
        
        آرگومان‌ها:
            config: شیء تنظیمات جستجو
        """
        self.config = config
        
        if DDGS is None:
            logger.warning("duckduckgo_search package is not installed. Install it with: pip install ddgs")
    
    def search(self, query: str, max_results: int = 3) -> List[SearchResult]:
        """
        Perform search using DuckDuckGo.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of SearchResult objects
            
        جستجو با استفاده از DuckDuckGo.
        
        آرگومان‌ها:
            query: رشته کوئری جستجو
            max_results: حداکثر تعداد نتایج
            
        بازگشت:
            فهرستی از اشیاء SearchResult
        """
        if DDGS is None:
            logger.error("duckduckgo_search package is required for DuckDuckGo provider")
            return []
        
        try:
            results = []
            ddgs = DDGS(timeout=10)
            
            # First attempt with default region
            search_results = ddgs.text(query, max_results=max_results)
            
            # Fallback to worldwide region if no results
            if not search_results:
                logger.info(f"No results for query '{query}', retrying with region='wt-wt'")
                search_results = ddgs.text(query, max_results=max_results, region="wt-wt")
            
            for item in search_results:
                result = SearchResult(
                    title=item.get("title", ""),
                    body=item.get("body", ""),
                    url=item.get("href", ""),
                    source_provider="DuckDuckGo"
                )
                results.append(result)
            
            return results
        
        except Exception as e:
            logger.error(f"Error searching with DuckDuckGo: {str(e)}")
            return []
