# voice/factory.py
"""
Factory Pattern برای TTS Providers
"""

from typing import Optional, Dict, Type
from enum import Enum
from core.voice.base import TTSProvider, TTSConfig
from core.voice.edge_tts_provider import EdgeTTSProvider
from core.voice.elevenlabs_provider import ElevenLabsProvider
from core.voice.gemini_provider import GeminiProvider


class TTSProviderType(Enum):
    """انواع TTS Providers"""
    EDGE_TTS = "edge_tts"
    ELEVENLABS = "elevenlabs"
    GEMINI = "gemini"


class TTSFactory:
    """
    Factory برای ایجاد TTS Provider instances
    
    استفاده:
        provider = TTSFactory.create(TTSProviderType.EDGE_TTS)
        audio_bytes = provider.synthesize("سلام")
    """

    _providers: Dict[TTSProviderType, Type[TTSProvider]] = {
        TTSProviderType.EDGE_TTS: EdgeTTSProvider,
        TTSProviderType.ELEVENLABS: ElevenLabsProvider,
        TTSProviderType.GEMINI: GeminiProvider,
    }

    @staticmethod
    def create(
        provider_type: TTSProviderType,
        api_key: Optional[str] = None,
        config: Optional[TTSConfig] = None,
    ) -> TTSProvider:
        """
        ایجاد یک TTS Provider
        
        Args:
            provider_type: نوع provider
            api_key: API Key (اگر لازم باشد)
            config: تنظیمات TTS
            
        Returns:
            TTSProvider: instance از provider
            
        Raises:
            ValueError: اگر نوع provider نامعتبر باشد
        """
        if provider_type not in TTSFactory._providers:
            raise ValueError(
                f"نوع provider نامعتبر: {provider_type}\n"
                f"انواع موجود: {[p.value for p in TTSProviderType]}"
            )

        provider_class = TTSFactory._providers[provider_type]

        # Edge TTS نیازمند API Key نیست
        if provider_type == TTSProviderType.EDGE_TTS:
            return provider_class(config=config)
        
        # سایر providers نیازمند API Key هستند
        if not api_key:
            raise ValueError(f"{provider_type.value} نیازمند API Key است")
        
        return provider_class(api_key=api_key, config=config)

    @staticmethod
    def get_available_providers() -> Dict[str, str]:
        """دریافت لیست providers موجود"""
        return {
            provider_type.value: provider_class.__doc__
            for provider_type, provider_class in TTSFactory._providers.items()
        }

    @staticmethod
    def register_provider(
        provider_type: TTSProviderType,
        provider_class: Type[TTSProvider],
    ) -> None:
        """
        ثبت یک provider سفارشی
        
        استفاده برای افزودن providers جدید:
            class CustomTTSProvider(TTSProvider):
                ...
            
            TTSFactory.register_provider(
                TTSProviderType.CUSTOM,
                CustomTTSProvider
            )
        """
        TTSFactory._providers[provider_type] = provider_class
