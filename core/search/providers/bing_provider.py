"""
Bing search provider implementation.
پیاده‌سازی سرویس‌دهنده جستجوی Bing.
"""

import logging
from typing import List
import requests
from ..base import BaseSearchProvider, SearchResult
from ..config import SearchConfig

logger = logging.getLogger(__name__)


class BingProvider(BaseSearchProvider):
    """
    Bing search provider implementation.
    Uses Azure Bing Web Search API.
    Requires BING_SEARCH_API_KEY in environment.
    
    پیاده‌سازی سرویس‌دهنده جستجوی Bing.
    از Azure Bing Web Search API استفاده می‌کند.
    نیاز به BING_SEARCH_API_KEY در محیط دارد.
    """
    
    API_URL = "https://api.bing.microsoft.com/v7.0/search"
    
    def __init__(self, config: SearchConfig):
        """
        Initialize Bing provider.
        
        Args:
            config: Search configuration object
            
        مقداردهی اولیه سرویس‌دهنده Bing.
        
        آرگومان‌ها:
            config: شیء تنظیمات جستجو
        """
        self.config = config
        self.api_key = config.bing_api_key
        
        if not self.api_key:
            logger.warning("BING_SEARCH_API_KEY is not set in environment variables")
    
    def search(self, query: str, max_results: int = 3) -> List[SearchResult]:
        """
        Perform search using Bing Search API.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of SearchResult objects
            
        جستجو با استفاده از Bing Search API.
        
        آرگومان‌ها:
            query: رشته کوئری جستجو
            max_results: حداکثر تعداد نتایج
            
        بازگشت:
            فهرستی از اشیاء SearchResult
        """
        if not self.api_key:
            logger.error("Bing API key is not configured")
            return []
        
        try:
            headers = {
                "Ocp-Apim-Subscription-Key": self.api_key
            }
            
            params = {
                "q": query,
                "count": max_results,
                "textDecorations": False,
                "textFormat": "HTML"
            }
            
            response = requests.get(
                self.API_URL,
                headers=headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get("webPages", {}).get("value", [])[:max_results]:
                result = SearchResult(
                    title=item.get("name", ""),
                    body=item.get("snippet", ""),
                    url=item.get("url", ""),
                    source_provider="Bing"
                )
                results.append(result)
            
            return results
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching with Bing: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in Bing search: {str(e)}")
            return []
