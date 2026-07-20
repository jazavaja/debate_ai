"""
Serper search provider implementation.
پیاده‌سازی سرویس‌دهنده جستجوی Serper (Google Search).
"""

import logging
from typing import List
import requests
from ..base import BaseSearchProvider, SearchResult
from ..config import SearchConfig

logger = logging.getLogger(__name__)


class SerperProvider(BaseSearchProvider):
    """
    Serper search provider implementation.
    Uses Google Search API through Serper.dev.
    Requires SERPER_API_KEY in environment.
    
    پیاده‌سازی سرویس‌دهنده جستجوی Serper.
    از API جستجوی Google از طریق Serper.dev استفاده می‌کند.
    نیاز به SERPER_API_KEY در محیط دارد.
    """
    
    API_URL = "https://google.serper.dev/search"
    
    def __init__(self, config: SearchConfig):
        """
        Initialize Serper provider.
        
        Args:
            config: Search configuration object
            
        مقداردهی اولیه سرویس‌دهنده Serper.
        
        آرگومان‌ها:
            config: شیء تنظیمات جستجو
        """
        self.config = config
        self.api_key = config.serper_api_key
        
        if not self.api_key:
            logger.warning("SERPER_API_KEY is not set in environment variables")
    
    def search(self, query: str, max_results: int = 3) -> List[SearchResult]:
        """
        Perform search using Serper API.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of SearchResult objects
            
        جستجو با استفاده از API Serper.
        
        آرگومان‌ها:
            query: رشته کوئری جستجو
            max_results: حداکثر تعداد نتایج
            
        بازگشت:
            فهرستی از اشیاء SearchResult
        """
        if not self.api_key:
            logger.error("Serper API key is not configured")
            return []
        
        try:
            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "q": query,
                "num": max_results
            }
            
            response = requests.post(
                self.API_URL,
                json=payload,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get("organic", [])[:max_results]:
                result = SearchResult(
                    title=item.get("title", ""),
                    body=item.get("snippet", ""),
                    url=item.get("link", ""),
                    source_provider="Serper"
                )
                results.append(result)
            
            return results
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching with Serper: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in Serper search: {str(e)}")
            return []
