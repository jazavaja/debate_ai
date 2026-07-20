# voice/manager.py
"""
Voice Manager - مدیریت TTS و تولید صوت
"""

import os
from typing import Optional, Dict
from core.voice.base import TTSProvider, TTSConfig
from core.voice.factory import TTSFactory, TTSProviderType
from core.voice.config import VoiceConfig


class VoiceManager:
    """
    مدیر مرکزی برای تمام عملیات صوتی
    """

    def __init__(self, config: Optional[VoiceConfig] = None):
        self.config = config or VoiceConfig()
        self._provider: Optional[TTSProvider] = None
        self._initialize_provider()

    def _initialize_provider(self) -> None:
        """مقدار دهی اولیه provider"""
        try:
            tts_config = TTSConfig(
                language="fa-IR",
                speed=self.config.speech_rate,
                pitch=self.config.pitch,
                volume=self.config.volume,
            )

            self._provider = TTSFactory.create(
                provider_type=self.config.provider_type,
                api_key=self._get_api_key_for_provider(),
                config=tts_config,
            )
        except Exception as e:
            raise RuntimeError(f"خطا در مقدار دهی TTS Provider: {str(e)}")

    def _get_api_key_for_provider(self) -> Optional[str]:
        """دریافت API Key برای provider فعلی"""
        if self.config.provider_type == TTSProviderType.EDGE_TTS:
            return None
        elif self.config.provider_type == TTSProviderType.ELEVENLABS:
            return self.config.elevenlabs_api_key
        elif self.config.provider_type == TTSProviderType.GEMINI:
            return self.config.gemini_api_key
        return None

    def synthesize_text(
        self,
        text: str,
        speaker_type: str = "moderator",
    ) -> bytes:
        """
        تبدیل متن به صوت
        
        Args:
            text: متن برای تبدیل
            speaker_type: نوع speaker (debater1, debater2, moderator)
            
        Returns:
            bytes: داده‌های صوتی
        """
        if not text or not text.strip():
            raise ValueError("متن نمی‌تواند خالی باشد")

        if not self._provider:
            raise RuntimeError("TTS Provider مقدار دهی نشده است")

        voice = self._get_voice_for_speaker(speaker_type)
        return self._provider.synthesize(text, speaker=voice)

    def _get_voice_for_speaker(self, speaker_type: str) -> str:
        """دریافت voice برای نوع speaker"""
        voice_mapping = {
            "debater1": self.config.debater1_voice,
            "debater2": self.config.debater2_voice,
            "moderator": self.config.moderator_voice,
        }
        return voice_mapping.get(speaker_type, self.config.moderator_voice)

    def save_audio(self, audio_data: bytes, filepath: str) -> None:
        """ذخیره داده‌های صوتی در فایل"""
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(audio_data)

    def get_available_voices(self) -> Dict[str, str]:
        """دریافت voice های موجود برای provider فعلی"""
        if not self._provider:
            raise RuntimeError("TTS Provider مقدار دهی نشده است")
        return self._provider.get_available_voices()

    def validate_credentials(self) -> bool:
        """بررسی صحت اعتبارات"""
        if not self._provider:
            return False
        return self._provider.validate_credentials()

    def switch_provider(
        self,
        provider_type: TTSProviderType,
        api_key: Optional[str] = None,
    ) -> None:
        """تبدیل به provider دیگر"""
        self.config.provider_type = provider_type
        
        if api_key:
            if provider_type == TTSProviderType.ELEVENLABS:
                self.config.elevenlabs_api_key = api_key
            elif provider_type == TTSProviderType.GEMINI:
                self.config.gemini_api_key = api_key
        
        self._initialize_provider()

    def update_voice_config(
        self,
        speech_rate: Optional[float] = None,
        pitch: Optional[float] = None,
        volume: Optional[float] = None,
        debater1_voice: Optional[str] = None,
        debater2_voice: Optional[str] = None,
        moderator_voice: Optional[str] = None,
    ) -> None:
        """به‌روزرسانی تنظیمات صوتی"""
        if speech_rate is not None:
            self.config.speech_rate = max(0.5, min(2.0, speech_rate))
        if pitch is not None:
            self.config.pitch = max(0.5, min(2.0, pitch))
        if volume is not None:
            self.config.volume = max(0.0, min(1.0, volume))
        if debater1_voice:
            self.config.debater1_voice = debater1_voice
        if debater2_voice:
            self.config.debater2_voice = debater2_voice
        if moderator_voice:
            self.config.moderator_voice = moderator_voice
        
        self._initialize_provider()

    def __repr__(self) -> str:
        return (
            f"VoiceManager("
            f"provider={self.config.provider_type.value}, "
            f"speech_rate={self.config.speech_rate}, "
            f"pitch={self.config.pitch})"
        )
