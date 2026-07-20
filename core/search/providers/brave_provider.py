"""
Brave search provider implementation.
پیاده‌سازی سرویس‌دهنده جستجوی Brave.
"""

import logging
from typing import List
import requests
from ..base import BaseSearchProvider, SearchResult
from ..config import SearchConfig

logger = logging.getLogger(__name__)


class BraveProvider(BaseSearchProvider):
    """
    Brave search provider implementation.
    Uses Brave Search API.
    Requires BRAVE_SEARCH_API_KEY in environment.
    
    پیاده‌سازی سرویس‌دهنده جستجوی Brave.
    از Brave Search API استفاده می‌کند.
    نیاز به BRAVE_SEARCH_API_KEY در محیط دارد.
    """
    
    API_URL = "https://api.search.brave.com/res/v1/web/search"
    
    def __init__(self, config: SearchConfig):
        """
        Initialize Brave provider.
        
        Args:
            config: Search configuration object
            
        مقداردهی اولیه سرویس‌دهنده Brave.
        
        آرگومان‌ها:
            config: شیء تنظیمات جستجو
        """
        self.config = config
        self.api_key = config.brave_api_key
        
        if not self.api_key:
            logger.warning("BRAVE_SEARCH_API_KEY is not set in environment variables")
    
    def search(self, query: str, max_results: int = 3) -> List[SearchResult]:
        """
        Perform search using Brave Search API.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of SearchResult objects
            
        جستجو با استفاده از Brave Search API.
        
        آرگومان‌ها:
            query: رشته کوئری جستجو
            max_results: حداکثر تعداد نتایج
            
        بازگشت:
            فهرستی از اشیاء SearchResult
        """
        if not self.api_key:
            logger.error("Brave API key is not configured")
            return []
        
        try:
            headers = {
                "Authorization": f"Token {self.api_key}",
                "Accept": "application/json"
            }
            
            params = {
                "q": query,
                "count": max_results
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
            
            for item in data.get("web", {}).get("results", [])[:max_results]:
                result = SearchResult(
                    title=item.get("title", ""),
                    body=item.get("description", ""),
                    url=item.get("url", ""),
                    source_provider="Brave"
                )
                results.append(result)
            
            return results
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching with Brave: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in Brave search: {str(e)}")
            return []
