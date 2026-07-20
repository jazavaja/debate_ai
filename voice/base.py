# voice/base.py
"""
Abstract Base Class برای Text-to-Speech
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class TTSConfig:
    """تنظیمات TTS"""
    language: str = "fa-IR"
    speed: float = 1.0
    pitch: float = 1.0
    volume: float = 1.0


class TTSProvider(ABC):
    """کلاس abstract برای تمام TTS providers"""

    def __init__(self, config: Optional[TTSConfig] = None):
        self.config = config or TTSConfig()

    @abstractmethod
    def synthesize(self, text: str, speaker: str = "default") -> bytes:
        """
        تبدیل متن به صوت
        
        Args:
            text: متن برای تبدیل به صوت
            speaker: شناسه یا نام speaker
            
        Returns:
            bytes: داده‌های صوتی (معمولاً MP3 یا WAV)
        """
        pass

    @abstractmethod
    def get_available_voices(self) -> dict:
        """
        دریافت لیست voice های موجود
        
        Returns:
            dict: {speaker_name: voice_id}
        """
        pass

    @abstractmethod
    def validate_credentials(self) -> bool:
        """بررسی صحت اعتبارات (API Key, etc.)"""
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(config={self.config})"
