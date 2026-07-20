# voice/edge_tts_provider.py
"""
Edge TTS Provider - استفاده از Microsoft Edge TTS
"""

import asyncio
import io
from typing import Optional
from core.voice.base import TTSProvider, TTSConfig


class EdgeTTSProvider(TTSProvider):
    """
    TTS Provider برای Microsoft Edge TTS
    نیازمند: pip install edge-tts
    """

    VOICES = {
        "fa-IR-DilaraNeural": "دیلارا",
        "fa-IR-FaridNeural": "فرید",
    }

    def __init__(self, config: Optional[TTSConfig] = None):
        super().__init__(config)
        self._validate_import()

    @staticmethod
    def _validate_import():
        """بررسی نصب edge-tts"""
        try:
            import edge_tts
        except ImportError:
            raise ImportError(
                "edge-tts نصب نشده است.\n"
                "برای نصب: pip install edge-tts"
            )

    def synthesize(self, text: str, speaker: str = "fa-IR-DilaraNeural") -> bytes:
        """
        تبدیل متن به صوت با Edge TTS
        
        Args:
            text: متن برای تبدیل
            speaker: voice ID (پیش‌فرض: دیلارا)
            
        Returns:
            bytes: داده‌های صوتی MP3
        """
        import edge_tts
        
        if not text or not text.strip():
            raise ValueError("متن نمی‌تواند خالی باشد")

        try:
            communicate = edge_tts.Communicate(
                text=text,
                voice=speaker,
                rate=f"+{int((self.config.speed - 1) * 50)}%",
                pitch=f"+{int((self.config.pitch - 1) * 50)}%",
            )
            
            audio_stream = io.BytesIO()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def _get_audio():
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_stream.write(chunk["data"])
            
            loop.run_until_complete(_get_audio())
            loop.close()
            
            return audio_stream.getvalue()
        except Exception as e:
            raise RuntimeError(f"خطا در تولید صوت Edge TTS: {str(e)}")

    def get_available_voices(self) -> dict:
        """دریافت voice های موجود"""
        return self.VOICES.copy()

    def validate_credentials(self) -> bool:
        """Edge TTS نیازمند credentials نیست"""
        try:
            self._validate_import()
            return True
        except ImportError:
            return False
