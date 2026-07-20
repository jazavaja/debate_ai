"""
Tavily search provider implementation.
پیاده‌سازی سرویس‌دهنده جستجوی Tavily.
"""

import logging
from typing import List
from ..base import BaseSearchProvider, SearchResult
from ..config import SearchConfig

try:
    from tavily import TavilyClient
except ImportError:
    TavilyClient = None

logger = logging.getLogger(__name__)


class TavilyProvider(BaseSearchProvider):
    """
    Tavily search provider implementation.
    Requires TAVILY_API_KEY in environment.
    
    پیاده‌سازی سرویس‌دهنده جستجوی Tavily.
    نیاز به TAVILY_API_KEY در محیط دارد.
    """
    
    def __init__(self, config: SearchConfig):
        """
        Initialize Tavily provider.
        
        Args:
            config: Search configuration object
            
        مقداردهی اولیه سرویس‌دهنده Tavily.
        
        آرگومان‌ها:
            config: شیء تنظیمات جستجو
        """
        self.config = config
        self.api_key = config.tavily_api_key
        self.client = None
        
        if TavilyClient is None:
            logger.warning("tavily package is not installed. Install it with: pip install tavily-python")
        elif not self.api_key:
            logger.warning("TAVILY_API_KEY is not set in environment variables")
        else:
            try:
                self.client = TavilyClient(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Tavily client: {str(e)}")
    
    def search(self, query: str, max_results: int = 3) -> List[SearchResult]:
        """
        Perform search using Tavily API.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of SearchResult objects
            
        جستجو با استفاده از API Tavily.
        
        آرگومان‌ها:
            query: رشته کوئری جستجو
            max_results: حداکثر تعداد نتایج
            
        بازگشت:
            فهرستی از اشیاء SearchResult
        """
        if self.client is None:
            logger.error("Tavily client is not initialized")
            return []
        
        try:
            response = self.client.search(
                query=query,
                max_results=max_results,
                include_answer=False
            )
            
            results = []
            for item in response.get("results", []):
                result = SearchResult(
                    title=item.get("title", ""),
                    body=item.get("content", ""),
                    url=item.get("url", ""),
                    source_provider="Tavily"
                )
                results.append(result)
            
            return results
        
        except Exception as e:
            logger.error(f"Error searching with Tavily: {str(e)}")
            return []
