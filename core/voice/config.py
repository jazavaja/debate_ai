# voice/config.py
"""
تنظیمات Voice/TTS
"""

from dataclasses import dataclass
from core.voice.factory import TTSProviderType


@dataclass
class VoiceConfig:
    """تنظیمات سیستم صدا"""
    
    # Provider اصلی
    provider_type: TTSProviderType = TTSProviderType.EDGE_TTS
    
    # API Keys
    elevenlabs_api_key: str = ""
    gemini_api_key: str = ""
    
    # تنظیمات صوتی
    speech_rate: float = 1.0  # 0.5 ~ 2.0
    pitch: float = 1.0  # 0.5 ~ 2.0
    volume: float = 1.0  # 0.0 ~ 1.0
    
    # Voice selection
    debater1_voice: str = "fa-IR-DilaraNeural"  # Edge TTS
    debater2_voice: str = "fa-IR-FaridNeural"   # Edge TTS
    moderator_voice: str = "fa-IR-DilaraNeural" # Edge TTS
    
    # خروجی
    output_format: str = "mp3"  # mp3, wav
    sample_rate: int = 44100  # Hz
    
    def to_dict(self) -> dict:
        """تبدیل به dictionary"""
        return {
            "provider_type": self.provider_type.value,
            "elevenlabs_api_key": self.elevenlabs_api_key,
            "gemini_api_key": self.gemini_api_key,
            "speech_rate": self.speech_rate,
            "pitch": self.pitch,
            "volume": self.volume,
            "debater1_voice": self.debater1_voice,
            "debater2_voice": self.debater2_voice,
            "moderator_voice": self.moderator_voice,
            "output_format": self.output_format,
            "sample_rate": self.sample_rate,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "VoiceConfig":
        """ایجاد از dictionary"""
        provider_type = TTSProviderType(data.get("provider_type", "edge_tts"))
        return cls(
            provider_type=provider_type,
            elevenlabs_api_key=data.get("elevenlabs_api_key", ""),
            gemini_api_key=data.get("gemini_api_key", ""),
            speech_rate=data.get("speech_rate", 1.0),
            pitch=data.get("pitch", 1.0),
            volume=data.get("volume", 1.0),
            debater1_voice=data.get("debater1_voice", "fa-IR-DilaraNeural"),
            debater2_voice=data.get("debater2_voice", "fa-IR-FaridNeural"),
            moderator_voice=data.get("moderator_voice", "fa-IR-DilaraNeural"),
            output_format=data.get("output_format", "mp3"),
            sample_rate=data.get("sample_rate", 44100),
        )
