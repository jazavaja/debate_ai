"""
Base classes and data structures for search providers.
کلاس‌های پایه و ساختارهای داده برای سرویس‌دهندگان جستجو.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass
class SearchResult:
    """
    Represents a single search result.
    نمایندگی یک نتیجه جستجوی تکی.
    """
    title: str
    body: str
    url: str
    source_provider: str


class BaseSearchProvider(ABC):
    """
    Abstract base class for all search providers.
    کلاس انتزاعی پایه برای تمام سرویس‌دهندگان جستجو.
    """

    @abstractmethod
    def search(self, query: str, max_results: int = 3) -> List[SearchResult]:
        """
        Perform a search query and return results.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of SearchResult objects
            
        جستجوی کوئری را انجام دهید و نتایج را برگردانید.
        
        آرگومان‌ها:
            query: رشته کوئری جستجو
            max_results: حداکثر تعداد نتایجی که باید برگردانده شوند
            
        بازگشت:
            فهرستی از اشیاء SearchResult
        """
        pass
