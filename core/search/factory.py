"""
Factory pattern implementation for creating search providers.
پیاده‌سازی الگوی Factory برای ایجاد سرویس‌دهندگان جستجو.
"""

from typing import Dict, Type
from .base import BaseSearchProvider
from .config import SearchConfig, SearchProviderType


class SearchFactory:
    """
    Factory class for creating search provider instances.
    کلاس Factory برای ایجاد نمونه‌های سرویس‌دهنده جستجو.
    """
    
    _providers: Dict[SearchProviderType, Type[BaseSearchProvider]] = {}
    
    @classmethod
    def register(cls, provider_type: SearchProviderType, provider_class: Type[BaseSearchProvider]) -> None:
        """
        Register a new search provider.
        
        Args:
            provider_type: The provider type enum value
            provider_class: The provider class to register
            
        ثبت یک سرویس‌دهنده جستجوی جدید.
        
        آرگومان‌ها:
            provider_type: مقدار enum نوع سرویس‌دهنده
            provider_class: کلاس سرویس‌دهنده برای ثبت
        """
        cls._providers[provider_type] = provider_class
    
    @classmethod
    def create(cls, provider_type: SearchProviderType, config: SearchConfig) -> BaseSearchProvider:
        """
        Create and return a search provider instance.
        
        Args:
            provider_type: The type of provider to create
            config: Search configuration object
            
        Returns:
            An instance of the requested search provider
            
        Raises:
            ValueError: If the provider type is not registered
            
        ایجاد و بازگشت نمونه‌ای از سرویس‌دهنده جستجو.
        
        آرگومان‌ها:
            provider_type: نوع سرویس‌دهنده برای ایجاد
            config: شیء تنظیمات جستجو
            
        بازگشت:
            نمونه‌ای از سرویس‌دهنده جستجوی درخواست‌شده
            
        می‌اندازد:
            ValueError: اگر نوع سرویس‌دهنده ثبت نشده باشد
        """
        if provider_type not in cls._providers:
            raise ValueError(f"Provider type '{provider_type.value}' is not registered")
        
        provider_class = cls._providers[provider_type]
        return provider_class(config)
    
    @classmethod
    def get_registered_providers(cls) -> list:
        """
        Get list of all registered provider types.
        
        Returns:
            List of registered SearchProviderType values
            
        دریافت فهرست تمام انواع سرویس‌دهندگان ثبت‌شده.
        
        بازگشت:
            فهرستی از مقادیر SearchProviderType ثبت‌شده
        """
        return list(cls._providers.keys())
